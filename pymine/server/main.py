#!/usr/bin/env python3

import uuid
import json
import asyncio
import websockets
import base64

import pprint

from dataclasses import replace

from typing import List, Dict, Tuple, Sequence

from pymine.server.encryption import EncryptionSession, AuthenticatedSession


async def minecraft_connection_handler(websocket, path):
    # authenticate session
    session = await enable_encryption(websocket, unauthenticated_session)

    print("Encrypted connection established!")

    # encoded_payload = base64.b64encode(
    #     session.encrypt(json.dumps(SAMPLE_PAYLOAD).encode("utf-8"))
    # ).decode()

    encoded_payload = session.encrypt_dict(SAMPLE_PAYLOAD)

    await websocket.send(encoded_payload)

    body = await websocket.recv()

    body_dec = session.decrypt(body)

    # print(f"< {body}")
    print(f"C< {body_dec}")

    __import__("sys").exit()


async def enable_encryption(
    websocket, session: EncryptionSession
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


def start_server(port: int = 19131):
    unauthenticated_session = EncryptionSession()

    print(f"Starting server on port {port}")

    minecraft_connection_server = websockets.serve(
        hello, "localhost", port, subprotocols=["com.microsoft.minecraft.wsencrypt"]
    )

    try:
        asyncio.get_event_loop().run_until_complete(minecraft_connection_server)
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    start_server()
