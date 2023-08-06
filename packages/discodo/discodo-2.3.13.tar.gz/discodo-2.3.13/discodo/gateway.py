import asyncio
import concurrent.futures
import json
import logging
import struct
import threading
import time
from collections import deque
from typing import Dict, Optional

import websockets

from .natives import Cipher

log = logging.getLogger("discodo.gateway")


class keepAliver(threading.Thread):
    def __init__(self, ws, interval: float, *args, **kwargs) -> None:
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True

        self.ws = ws
        self.interval: float = interval
        self.Stopped = threading.Event()
        self.latency: Optional[float] = None
        self.recent_latencies = deque(maxlen=20)

        self._lastAck = self._lastSend = time.perf_counter()
        self.timeout: float = ws.heartbeatTimeout
        self.threadId: int = ws.threadId

    def __del__(self) -> None:
        self.stop()

    def run(self) -> None:
        while not self.Stopped.wait(self.interval):
            if (self._lastAck + self.timeout) < time.perf_counter():
                Runner = asyncio.run_coroutine_threadsafe(
                    self.ws.close(4000), self.ws.loop
                )

                try:
                    Runner.result()
                except:
                    pass

                self.stop()
                return

            payload: Dict[str, int] = {
                "op": VoicePayload.HEARTBEAT,
                "d": int(time.time() * 1000),
            }
            Runner = asyncio.run_coroutine_threadsafe(
                self.ws.sendJson(payload), self.ws.loop
            )
            try:
                totalBlocked: int = 0
                while True:
                    try:
                        Runner.result(10)
                        break
                    except concurrent.futures.TimeoutError:
                        totalBlocked += 10
                        log.warning(
                            f"Thread-{self.threadId}: Heartbeat blocked for more than {totalBlocked} seconds."
                        )
            except:
                return self.stop()
            else:
                self._lastSend = time.perf_counter()

    def ack(self) -> None:
        self._lastAck = time.perf_counter()
        self.latency = self._lastAck - self._lastSend
        self.recent_latencies.append(self.latency)

    def stop(self) -> None:
        self.Stopped.set()


class VoicePayload:
    IDENTIFY = 0
    SELECT_PROTOCOL = 1
    READY = 2
    HEARTBEAT = 3
    SESSION_DESCRIPTION = 4
    SPEAKING = 5
    HEARTBEAT_ACK = 6
    RESUME = 7
    HELLO = 8
    RESUMED = 9
    CLIENT_DISCONNECT = 13


class VoiceSocket(websockets.client.WebSocketClientProtocol):
    def __del__(self) -> None:
        self.loop.call_soon_threadsafe(lambda: self.loop.create_task(self.close()))

    @classmethod
    async def connect(cls, client, resume=False):
        ws = await websockets.connect(
            f"wss://{client.endpoint}/?v=4",
            loop=client.loop,
            klass=cls,
            compression=None,
        )

        ws.client = client
        ws.keepAliver = None
        ws.heartbeatTimeout = 60.0
        ws.threadId = threading.get_ident()

        if not resume:
            await ws.identify()
        else:
            await ws.resume()

        return ws

    @property
    def latency(self) -> Optional[float]:
        return self.keepAliver.latency if self.keepAliver else None

    @property
    def averageLatency(self) -> Optional[float]:
        if not self.keepAliver:
            return None

        return sum(self.keepAliver.recent_latencies) / len(
            self.keepAliver.recent_latencies
        )

    async def sendJson(self, data: dict) -> None:
        log.debug(f"send to websocket {data}")
        await self.send(json.dumps(data))

    async def identify(self) -> None:
        payload = {
            "op": VoicePayload.IDENTIFY,
            "d": {
                "server_id": str(self.client.guild_id),
                "user_id": str(self.client.user_id),
                "session_id": self.client.session_id,
                "token": self.client.token,
            },
        }
        await self.sendJson(payload)

    async def resume(self) -> None:
        payload = {
            "op": VoicePayload.RESUME,
            "d": {
                "server_id": str(self.client.guild_id),
                "user_id": str(self.client.user_id),
                "session_id": self.client.session_id,
                "token": self.client.token,
            },
        }
        await self.sendJson(payload)

    async def select_protocol(self, ip: str, port: str, mode: str) -> None:
        payload = {
            "op": VoicePayload.SELECT_PROTOCOL,
            "d": {
                "protocol": "udp",
                "data": {"address": ip, "port": port, "mode": mode},
            },
        }
        await self.sendJson(payload)

    async def speak(self, state: bool = True) -> None:
        self.client.speakState = state

        payload = {
            "op": VoicePayload.SPEAKING,
            "d": {"speaking": int(state), "delay": 0, "ssrc": self.client.ssrc},
        }
        await self.sendJson(payload)

    async def messageRecieved(self, message: dict) -> None:
        Operation, Data = message["op"], message.get("d")
        log.debug(f"websocket recieved {Operation}: {Data}")

        if Operation == VoicePayload.READY:
            await self.createConnection(Data)
        elif Operation == VoicePayload.HEARTBEAT_ACK:
            self.keepAliver.ack()
        elif Operation == VoicePayload.SESSION_DESCRIPTION:
            await self.loadKey(Data)
        elif Operation == VoicePayload.HELLO:
            interval = Data["heartbeat_interval"] / 1000.0
            self.keepAliver = keepAliver(self, min(interval, 5.0))
            self.keepAliver.start()

    async def createConnection(self, data: Optional[dict]) -> None:
        self.client.ssrc = data["ssrc"]
        self.client.endpointIp = data["ip"]
        self.client.endpointPort = data["port"]

        packet = bytearray(70)
        struct.pack_into(">I", packet, 0, data["ssrc"])

        self.client.socket.sendto(
            packet, (self.client.endpointIp, self.client.endpointPort)
        )
        _recieved = await self.loop.sock_recv(self.client.socket, 70)

        start, end = 4, _recieved.index(0, 4)
        self.client.ip = _recieved[start:end].decode("ascii")
        self.client.port = struct.unpack_from(">H", _recieved, len(_recieved) - 2)[0]

        encryptModes = [Mode for Mode in data["modes"] if Mode in Cipher.available]
        log.debug(f'recieved encrypt modes {data["modes"]}')

        encryptMode = encryptModes[0]
        log.info(f"select encrypt mode {encryptMode}")

        await self.select_protocol(self.client.ip, self.client.port, encryptMode)

    async def loadKey(self, data: Optional[dict]) -> None:
        log.info("recieved voice secret key.")

        self.client.speakState = False

        self.client.encryptMode = data["mode"]
        self.client.secretKey = data.get("secret_key")

    async def poll(self) -> None:
        message = await asyncio.wait_for(self.recv(), timeout=30.0)
        await self.messageRecieved(json.loads(message))

    async def close(self, *args, **kwargs) -> None:
        if self.keepAliver:
            self.keepAliver.stop()

        await super().close(*args, **kwargs)
