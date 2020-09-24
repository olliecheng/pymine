#!/usr/bin/env python3
#
#   The Bridge connector, which allows for external applications to communicate
#   with the server. Currently supports websocket connections.
#
#  A part of denosawr/pymine


import asyncio
import websockets

from typing import List

from .base import Connector

from pymine.utils.logging import getLogger

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
        send_queue: asyncio.Queue,
        recv_queue: asyncio.Queue,
        host: str = "localhost",
        port: int = 19132,
    ):
        self.host = host
        self.port = port

        self.send_queue = send_queue
        self.recv_queue = recv_queue

        self.broadcast_queues = []

    def start(self, loop: asyncio.BaseEventLoop):
        loop.create_task(
            self.broadcast_announcer(self.broadcast_queues, self.send_queue)
        )
        self.ws = websockets.serve(
            lambda ws, p: self.handler(ws, p), self.host, self.port, loop=loop
        )

        loop.run_until_complete(self.ws)
        log.debug("Started websocket server.")

    async def handler(self, websocket, path):
        "Handles individual websocket requests."

        broadcast_queue = asyncio.Queue()
        self.broadcast_queues.append(broadcast_queue)

        command_task = asyncio.ensure_future(
            self.command_handler(websocket, path, self.recv_queue)
        )
        broadcast_task = asyncio.ensure_future(
            self.broadcast_handler(websocket, path, broadcast_queue)
        )

        _done, pending = await asyncio.wait(
            [command_task, broadcast_task], return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

        # TODO: graceful cleanup, remove from broadcast queue

    @staticmethod
    async def broadcast_announcer(
        broadcast_queues: List[asyncio.Queue], send_queue: asyncio.Queue
    ):
        """
        Announces MC responses to all individual websocket connections.
        Does not send any network requests; self.broadcast_handler will receive
        and process announcements.
        """

        while True:
            response = await send_queue.get()

            for q in broadcast_queues:
                await q.put(response)

    @staticmethod
    async def command_handler(websocket, path, queue: asyncio.Queue):
        "Receives external commands and adds to the queue."

        async for message in websocket:
            print(f"Command recv: {message}")
            await queue.put(message)

    @staticmethod
    async def broadcast_handler(websocket, path, queue: asyncio.Queue):
        """
        Broadcasts messages to individual websocket connections.
        Messages come from announcements by self.broadcast_announcer.
        """

        while True:
            response: str = await queue.get()

            await websocket.send(response)
