import sys
from .datatypes import Target, Position
from .data import mobs, items, blocks
from .exceptions import EventTimeout

import time
import pprint
import json

import inspect
import asyncio
import websockets
import uuid

from typing import Optional


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
                else:
                    response_raw = (await ws.recv()).decode()

                response = json.loads(response_raw)

                if response["body"].get("eventName", "") != event_name:
                    continue

                if inspect.iscoroutinefunction(filter_func):
                    # if is a coroutine
                    filter_result = await filter_func(response["body"])
                else:
                    filter_result = await asyncio.get_running_loop().run_in_executor(
                        None, filter_func, response["body"]
                    )

                if filter_result:
                    await complete()
                    return response

        except asyncio.TimeoutError:
            await complete()
            raise EventTimeout


def wait_for_event(event_name: str, filter_func=lambda x: True, timeout: int = 0):
    return asyncio.get_event_loop().run_until_complete(
        async_wait_for_event(event_name, filter_func, timeout)
    )


# def wait_for_player_movement(position: Optional[Position] = None):
def wait_for_player_movement(
    check_x: Optional[int] = None,
    check_y: Optional[int] = None,
    check_z: Optional[int] = None,
    check_radius: int = 1,
):
    def filter_func(r):
        nonlocal check_x, check_y, check_z

        for dim in ("x", "y", "z"):
            check: int = locals()[f"check_{dim}"]

            if (
                check != None
                and abs(r["measurements"][f"PosAvg{dim.upper()}"] - check)
                > check_radius
            ):
                # print("nope", r, check)
                return False
        return True

    wait_for_event("PlayerTravelled", filter_func)

