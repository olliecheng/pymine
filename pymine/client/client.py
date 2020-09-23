import websockets
import uuid
import json
import asyncio


SAMPLE_PAYLOAD = {
    "body": {"commandLine": "say hello"},
    "header": {
        "requestId": str(uuid.uuid1()),
        "messagePurpose": "commandRequest",
        "version": 1,
    },
}


async def amain():
    uri = "ws://localhost:19132"
    async with websockets.connect(uri) as ws:
        text = json.dumps(SAMPLE_PAYLOAD)
        await ws.send(text)
        print("Sent!")

        result = await ws.recv()
        print(result)


def main():
    asyncio.run(amain())


if __name__ == "__main__":
    main()
