import websockets
import asyncio

from typing import List

from .template import Connector


class WSBridgeConnector(Connector):
    def __init__(self, send_queue: asyncio.Queue, recv_queue: asyncio.Queue, host: str = "localhost", port: int = 19132):
        self.host = host
        self.port = port

        self.send_queue = send_queue
        self.recv_queue = recv_queue

        self.broadcast_queues = []

    async def handler(self, websocket, path):
        broadcast_queue = asyncio.Queue()
        self.broadcast_queues.append(broadcast_queue)

        command_task = asyncio.ensure_future(
            self.command_handler(websocket, path, self.recv_queue)
        )
        broadcast_task = asyncio.ensure_future(
            self.broadcast_handler(websocket, path, broadcast_queue)
        )

        done, pending = await asyncio.wait(
            [command_task, broadcast_task],
            return_when=asyncio.FIRST_COMPLETED,
        )

        for task in pending:
            task.cancel()

    @staticmethod
    async def command_handler(websocket, path, queue: asyncio.Queue):
        async for message in websocket:
            print(f"Command recv: {message}")
            await queue.put(message)

    @staticmethod
    async def broadcast_handler(websocket, path, queue: asyncio.Queue):
        while True:
            response: str = await queue.get()

            await websocket.send(response)

    @staticmethod
    async def broadcast_announcer(broadcast_queues: List[asyncio.Queue], send_queue: asyncio.Queue):
        while True:
            response = await send_queue.get()

            for q in broadcast_queues:
                await q.put(response)

    def start(self, loop: asyncio.BaseEventLoop):
        loop.create_task(self.broadcast_announcer(
            self.broadcast_queues, self.send_queue)
        )
        self.ws = websockets.serve(
            lambda ws, p: self.handler(ws, p),
            self.host,
            self.port,
            loop=loop
        )
        loop.run_until_complete(self.ws)
