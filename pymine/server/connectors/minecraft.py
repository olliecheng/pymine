#!/usr/bin/env python3
#
#   The Minecraft connector, which allows for communication via encrypted websocket
#   with a Minecraft: Bedrock Edition client. Runs a WS server and transparently
#   authenticates (upgrade to an encrypted connection) and performs transparent
#   encryption and decryption.
#
#  A part of denosawr/pymine

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


# fmt: off
class AuthenticationError(Exception):
    pass
class TimeoutAuthenticationError(AuthenticationError):
    pass
class RefusedAuthenticationError(AuthenticationError):
    pass
# fmt: on


class MinecraftConnector(Connector):
    """
    Connects an instance of Minecraft: Bedrock Edition with the queues.

    Key parameters:
      send_queue: A queue of responses from MC
      recv_queue: A queue of commands to send to MC

    Warnings:
      Can only accept one simultaneous connection request.
    """

    def __init__(
        self,
        send_queue: asyncio.Queue,
        recv_queue: asyncio.Queue,
        host: str = "localhost",
        port: int = 19131,
    ):
        # generate new EncryptionSession, unique to this instance of the Connector.
        self.unauthenticated_session = EncryptionSession()

        self.host = host
        self.port = port

        self.send_queue = send_queue
        self.recv_queue = recv_queue

    async def handler(self, websocket, path):
        log.debug("Received connection request.")

        # Check only one connection occurs at a time
        if websocket.sockets != 1:
            # this connection must be the extra socket!
            log.error("Received second connection request, this has been refused.")
            return

        # Upgrade connection immediately upon connection
        try:
            session = await self.enable_encryption(
                websocket, self.unauthenticated_session
            )
        except AuthenticationError as err:
            log.error(f"Could not authenticate: {err}")
            return

        log.debug("Encrypted connection established, now listening for updates...")

        # register tasks
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
        "Processes responses from Minecraft."

        async for message_encrypted in websocket:
            message = session.decrypt(message_encrypted)

            await queue.put(message)

    @staticmethod
    async def send_handler(
        websocket, path, session: EncryptionSession, queue: asyncio.Queue
    ):
        "Processes requests to Minecraft."

        while True:
            request: str = await queue.get()

            payload = session.encrypt(request.encode())
            await websocket.send(payload)

    @staticmethod
    async def enable_encryption(
        websocket, session: EncryptionSession
    ) -> AuthenticatedSession:
        "Negotiates the authentication handshake."

        # generate a unique request ID for the payload
        requestId = str(uuid.uuid1())

        authentication_payload = {
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

        await websocket.send(json.dumps(authentication_payload))

        # check that the response has a matching requestId
        for _ in range(3):
            response = json.loads(await websocket.recv())

            if response["header"]["requestId"] == requestId:
                break
        else:
            raise TimeoutAuthenticationError(
                "Not responding to unique request ID. "
                + "Check it's not busy with requests from multiple instances?"
            )

        try:
            public_key = base64.b64decode(response["body"]["publicKey"])
        except KeyError:
            raise RefusedAuthenticationError(
                f"Connection was refused. Response:\n{pprint.pformat(response)}"
            )

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
