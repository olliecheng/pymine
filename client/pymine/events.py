import sys
from .datatypes import Target, Pos
from .data import mobs, items, blocks
from .exceptions import EventTimeout

import time
import pprint
import json

import inspect
import asyncio
import websockets
import uuid


async def async_wait_for_event(
    event_name: str, filter_func=lambda x: True, timeout: int = 0
):
    PAYLOAD = {
        "body": {"eventName": event_name},
        "header": {
            "requestId": str(uuid.uuid1()),
            "messagePurpose": "subscribe",
            "version": 1,
            "messageType": "commandRequest",
        },
    }

    async with websockets.connect("ws://localhost:19132") as ws:
        await ws.send(json.dumps(PAYLOAD))

        async def complete():
            PAYLOAD["header"]["messagePurpose"] = "unsubscribe"
            PAYLOAD["header"]["requestId"] = str(uuid.uuid1())

            await ws.send(json.dumps(PAYLOAD))

        start_time = time.time()
        try:
            while True:
                if timeout:
                    time_left = timeout - (time.time() - start_time)

                    if time_left < 0:
                        raise asyncio.TimeoutError

                    response_raw: str = (
                        await asyncio.wait_for(ws.recv(), timeout=time_left)
                    ).decode()

                    print("ok")
                else:
                    response_raw = (await ws.recv()).decode()

                response = json.loads(response_raw)

                if response["body"].get("eventName", "") != event_name:
                    continue

                elif filter_func(response):
                    await complete()
                    return response

        except asyncio.TimeoutError:
            await complete()
            raise EventTimeout


def wait_for_event(event_name: str, filter_func=lambda x: True, timeout: int = 0):
    return asyncio.run(async_wait_for_event(event_name, filter_func, timeout))
