#!/usr/bin/env python3

import uuid
import json
import asyncio
import websockets

from typing import List, Dict, Tuple, Sequence

import server.encryption as encryption


async def enable_encryption(websocket, encryption_session: encryption):
    requestId = str(uuid.uuid1())
    encrypted_payload = {
        "body": {
            "commandLine": 'enableencryption "{public_key}" "{salt}"'.format(
                public_key=encryption_session.b64_public_key,
                salt=encryption_session.b64_salt
            ),
            "version": 1
        },
        "header": {
            "requestId": requestId,
            "messagePurpose": "commandRequest",
            "version": 1
        }
    }

    await websocket.send(json.dumps(encrypted_payload))

    for _ in range(3):
        response = json.loads(await websocket.recv())

        if response["header"]["requestId"] == requestId:
            break
    else:
        raise ConnectionError(
            "Server not responding to unique request ID. " +
            "Check it's not busy with multiple instances?"
        )

    encryption_session.client_public_key = response["body"]["publicKey"]


def start_server(port: int = 19131):
    encryption_session = encryption.EncryptionSession()

    async def hello(websocket, path):
        await enable_encryption(websocket, encryption_session)

        print("Encrypted connection established!")

        body = await websocket.recv()

        body_dec = encryption_session.decrypt(body.encode("utf-8"))

        print(f"< {body}")
        # print(f"C< {body_dec}")

    print(f"Starting server on port {port}")

    server = websockets.serve(hello, "localhost", port, subprotocols=[
        "com.microsoft.minecraft.wsencrypt"])

    try:
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    start_server()
