#!/usr/bin/env python3

import uuid
import json
import asyncio
import websockets
import base64

from dataclasses import replace

from typing import List, Dict, Tuple, Sequence

from pymine.server.encryption import EncryptionSession


async def enable_encryption(websocket, session: EncryptionSession) -> EncryptionSession:
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

    public_key = base64.b64decode(response["body"]["publicKey"])

    return replace(
        session,
        client_public_key=public_key,
        authenticated=True,
        shared_secret=EncryptionSession.compute_shared_secret(public_key),
    )


def start_server(port: int = 19131):
    unauthenticated_session = EncryptionSession()

    SAMPLE_PAYLOAD = {
        "body": {"commandLine": "say hello"},
        "header": {
            "requestId": str(uuid.uuid1()),
            "messagePurpose": "commandRequest",
            "version": 1,
        },
    }

    async def hello(websocket, path):
        # authenticate session
        session = await enable_encryption(websocket, unauthenticated_session)

        print("Encrypted connection established!")

        # encoded_payload = base64.b64encode(
        #     session.encrypt(json.dumps(SAMPLE_PAYLOAD).encode("utf-8"))
        # ).decode()

        encoded_payload = session.encrypt(json.dumps(SAMPLE_PAYLOAD).encode())

        print(type(encoded_payload))

        # TODO: abstract sending as text frame

        # wait until all fragments have completed
        await websocket.ensure_open()
        while websocket._fragmented_message_waiter is not None:
            await asyncio.shield(websocket._fragmented_message_waiter)

        # send payload as text frame
        await websocket.write_frame(True, 0x01, encoded_payload)

        # await websocket.send(encoded_payload)

        print(f"Sent! {encoded_payload}")

        body = await websocket.recv()
        print(body)

        body_dec = session.decrypt(body.encode("utf-8"))

        # print(f"< {body}")
        print(f"C< {body_dec}")

    print(f"Starting server on port {port}")

    server = websockets.serve(
        hello, "localhost", port, subprotocols=["com.microsoft.minecraft.wsencrypt"]
    )

    try:
        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    start_server()
