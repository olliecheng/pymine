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

from .base import Connector, Publisher


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
        publisher: Publisher,
        recv_queue: asyncio.Queue,
        host: str = "localhost",
        port: int = 19131,
    ):
        # generate new EncryptionSession, unique to this instance of the Connector.
        self.unauthenticated_session = EncryptionSession()

        self.host = host
        self.port = port

        self.publisher = publisher
        self.recv_queue = recv_queue

        self.connection_lock = asyncio.Lock()

        self.error_handler = None

    async def set_uninitiated_handler_status(self, ready: bool):
        if ready and self.error_handler:
            log.debug("Cancelling uninitiated_handler")
            self.error_handler.cancel()
        else:
            self.error_handler = asyncio.create_task(
                self.uninitiated_handler(self.recv_queue, self.publisher)
            )

    async def uninitiated_handler(
        self, recv_queue: asyncio.Queue, publisher: Publisher
    ):
        "Processes requests to Minecraft before a connection is made i.e. denies the requests."

        log.debug("Starting uninitiated_handler")

        while True:
            request_str: str = await recv_queue.get()
            request = json.loads(request_str)
            log.debug(f"Received request: {request}")

            response_payload = {
                "body": {"error": "minecraft-not-connected"},
                "header": {
                    "messagePurpose": "commandResponse",
                    "requestId": request["header"]["requestId"],
                    "version": 1,
                },
            }

            publisher.publish(json.dumps(response_payload))

    async def handler(self, websocket, path):
        # Check only one connection occurs at a time
        if self.connection_lock.locked():
            log.error("Received second connection request, this has been refused.")
            return

        async with self.connection_lock:
            log.debug("Received connection request.")

            # Upgrade connection immediately upon connection
            try:
                session = await self.enable_encryption(
                    websocket, self.unauthenticated_session
                )
            except AuthenticationError as err:
                log.error(f"Could not authenticate: {err}")
                return

            log.debug("Encrypted connection established, now listening for updates...")
            log.info("Connected to Minecraft!")

            await self.set_uninitiated_handler_status(True)

            # register tasks
            receive_task = asyncio.ensure_future(
                self.recv_handler(websocket, path, session, self.publisher)
            )
            send_task = asyncio.ensure_future(
                self.send_handler(websocket, path, session, self.recv_queue)
            )

            _done, pending = await asyncio.wait(
                [receive_task, send_task], return_when=asyncio.FIRST_COMPLETED,
            )

            # should never need to run...
            # TODO: close queues on completion
            for task in pending:
                task.cancel()

    @staticmethod
    async def recv_handler(
        websocket, path, session: EncryptionSession, publisher: Publisher
    ):
        "Processes responses from Minecraft."

        async for message_encrypted in websocket:
            message = session.decrypt(message_encrypted)

            publisher.publish(message)

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
        ws_future = websockets.serve(
            lambda ws, p: self.handler(ws, p),
            self.host,
            self.port,
            subprotocols=["com.microsoft.minecraft.wsencrypt"],
            ping_interval=None,
            loop=loop,
        )
        self.ws = loop.run_until_complete(ws_future)
        loop.run_until_complete(self.set_uninitiated_handler_status(ready=False))

        log.info(f"Started Minecraft connector on {self.host}:{self.port}")
