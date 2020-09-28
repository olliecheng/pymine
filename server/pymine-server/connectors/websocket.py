#!/usr/bin/env python3
#
#   The Bridge connector, which allows for external applications to communicate
#   with the server. Currently supports websocket connections.
#
#  A part of denosawr/pymine


import asyncio
import websockets

from typing import List

from ..base import Connector, Publisher
from ..utils.logging import getLogger

log = getLogger("connectors.bridge")


class WSBridgeConnector(Connector):
    """
    Connects an external websocket with the queues.

    Key parameters:
      send_queue: A queue of responses from MC
      recv_queue: A queue of commands to send to MC
    """

    def __init__(
        self,
        publisher: Publisher,
        recv_queue: asyncio.Queue,
        host: str = "localhost",
        port: int = 19132,
    ):
        self.host = host
        self.port = port

        self.publisher = publisher
        self.recv_queue = recv_queue

    def start(self, loop: asyncio.BaseEventLoop):
        self.ws = websockets.serve(
            lambda ws, p: self.handler(ws, p), self.host, self.port, loop=loop
        )

        loop.run_until_complete(self.ws)
        log.debug("Started websocket server.")
        log.info(f"Started websocket bridge on {self.host}:{self.port}")

    async def handler(self, websocket, path):
        "Handles individual websocket requests."

        command_task = asyncio.ensure_future(
            self.command_handler(websocket, path, self.recv_queue)
        )
        subscription_task = asyncio.ensure_future(
            self.subscription_handler(websocket, path, self.publisher)
        )

        _done, pending = await asyncio.wait(
            [command_task, subscription_task], return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

    @staticmethod
    async def command_handler(websocket, path, queue: asyncio.Queue):
        "Receives external commands and adds to the queue."

        async for message in websocket:
            print(f"Command recv: {message}")
            await queue.put(message)

    @staticmethod
    async def subscription_handler(websocket, path, publisher: Publisher):
        """
        Creates a new subscription to the queue and forwards all announcements
        to the websocket.
        """

        with publisher.subscription() as queue:
            while True:
                response: str = await queue.get()

                await websocket.send(response)
