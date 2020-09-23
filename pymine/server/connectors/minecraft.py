#!/usr/bin/env python3

import asyncio
import base64
import json
import pprint
import uuid
import websockets

from typing import List, Dict, Tuple, Sequence

from pymine.utils.logging import getLogger
from pymine.server.encryption import EncryptionSession, AuthenticatedSession

from .template import Connector


log = getLogger("connectors.minecraft")

SAMPLE_PAYLOAD = {
    "body": {"commandLine": "say hello"},
    "header": {
        "requestId": str(uuid.uuid1()),
        "messagePurpose": "commandRequest",
        "version": 1,
    },
}


# fmt: off
class AuthenticationError(Exception):
    pass
class TimeoutAuthenticationError(AuthenticationError):
    pass
class RefusedAuthenticationError(AuthenticationError):
    pass
# fmt: on


class MinecraftConnector(Connector):
    def __init__(
        self,
        send_queue: asyncio.Queue,
        recv_queue: asyncio.Queue,
        host: str = "localhost",
        port: int = 19131,
    ):
        self.unauthenticated_session = EncryptionSession()

        self.host = host
        self.port = port

        self.send_queue = send_queue
        self.recv_queue = recv_queue

    async def handler(self, websocket, path):
        try:
            session = await self.enable_encryption(
                websocket, self.unauthenticated_session
            )
        except AuthenticationError:
            return

        log.debug("Encrypted connection established, now listening for updates...")

        receive_task = asyncio.ensure_future(
            self.recv_handler(websocket, path, session, self.send_queue)
        )
        send_task = asyncio.ensure_future(
            self.send_handler(websocket, path, session, self.recv_queue)
        )

        _done, pending = await asyncio.wait(
            [receive_task, send_task], return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

    @staticmethod
    async def recv_handler(
        websocket, path, session: EncryptionSession, queue: asyncio.Queue
    ):
        async for message_encrypted in websocket:
            message = session.decrypt(message_encrypted)

            await queue.put(message)

    @staticmethod
    async def send_handler(
        websocket, path, session: EncryptionSession, queue: asyncio.Queue
    ):
        while True:
            request: str = await queue.get()

            payload = session.encrypt(request.encode())
            await websocket.send(payload)

    async def enable_encryption(
        self, websocket, session: EncryptionSession
    ) -> AuthenticatedSession:
        requestId = str(uuid.uuid1())

        encrypted_payload = {
            "body": {
                "commandLine": 'enableencryption "{public_key}" "{salt}"'.format(
                    public_key=session.b64_public_key, salt=session.b64_salt,
                ),
                "version": 1,
            },
            "header": {
                "requestId": requestId,
                "messagePurpose": "commandRequest",
                "version": 1,
            },
        }

        await websocket.send(json.dumps(encrypted_payload))

        for _ in range(3):
            response = json.loads(await websocket.recv())

            if response["header"]["requestId"] == requestId:
                break
        else:
            log.error(
                "Could not authenticate: not responding to unique request ID. "
                + "Check it's not busy with requests from multiple instances?"
            )
            raise TimeoutAuthenticationError

        try:
            public_key = base64.b64decode(response["body"]["publicKey"])
        except KeyError:
            log.debug(pprint.pformat(response))
            log.error("Could not authenticate: MC refused connection.")
            raise RefusedAuthenticationError

        return AuthenticatedSession(session, public_key)

    def start(self, loop: asyncio.BaseEventLoop):
        self.ws = websockets.serve(
            lambda ws, p: self.handler(ws, p),
            self.host,
            self.port,
            subprotocols=["com.microsoft.minecraft.wsencrypt"],
            ping_interval=None,
            loop=loop,
        )
        loop.run_until_complete(self.ws)
        log.debug("Started websocket server.")
