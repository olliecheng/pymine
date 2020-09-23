#!/usr/bin/env python3

import uuid
import json
import asyncio
import websockets
import base64

import asyncio

import pprint

from dataclasses import replace

from typing import List, Dict, Tuple, Sequence

from pymine.server.encryption import EncryptionSession, AuthenticatedSession

SAMPLE_PAYLOAD = {
    "body": {"commandLine": "say hello"},
    "header": {
        "requestId": str(uuid.uuid1()),
        "messagePurpose": "commandRequest",
        "version": 1,
    },
}


class MinecraftConnector:
    def __init__(self, path: str = "localhost", port: int = 19131, callback):
        self.ws = websockets.serve(
            lambda ws, p: self.handler(ws, p)
            path,
            port,
            subprotocols=["com.microsoft.minecraft.wsencrypt"],
        )
        self.unauthenticated_session = EncryptionSession()

        self.callback = callback

    async def handler(self, websocket, path):
        # authenticate session
        session = await self.enable_encryption(websocket, self.unauthenticated_session)
        print("Encrypted connection established!")

        consumer_task = asyncio.ensure_future(
            self.receive_handler(websocket, path, session)
        )
        producer_task = asyncio.ensure_future(
            producer_handler(websocket, path)
        )

        done, pending = await asyncio.wait(
            [consumer_task, producer_task],
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in pending:
            task.cancel()


        encoded_payload = self.session.encrypt_dict(SAMPLE_PAYLOAD)
        await websocket.send(encoded_payload)

        body = await websocket.recv()

        body_dec = self.session.decrypt(body)

        # print(f"< {body}")
        print(f"C< {body_dec}")

        __import__("sys").exit()

    @staticmethod
    async def receive_handler(websocket, path, session: AuthenticatedSession):
        async for message_encrypted in websocket:
            message = session.decrypt(message_encrypted)
            


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
            raise ConnectionError(
                "Server not responding to unique request ID. "
                + "Check it's not busy with multiple instances?"
            )

        try:
            public_key = base64.b64decode(response["body"]["publicKey"])
        except KeyError:
            pprint.pprint(response)

        return AuthenticatedSession(session, public_key)

    def run_until_complete(self, event_loop: asyncio.BaseEventLoop):
        event_loop.run_until_complete(self.ws)

