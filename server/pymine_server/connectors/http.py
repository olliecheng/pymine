import asyncio
import json
import uuid
import time
from aiohttp import web

from ..utils.logging import getLogger
from ..base import Connector, Publisher

log = getLogger("connectors.http")
# log.setLevel("DEBUG")


class HTTPConnector(Connector):
    def __init__(
        self,
        publisher: Publisher,
        recv_queue: asyncio.Queue,
        host: str = "localhost",
        port: int = 19133,
    ):
        self.publisher = publisher
        self.recv_queue = recv_queue
        self.host = host
        self.port = port

    async def handler(self, request: web.Request):
        start_time = time.time()

        command = request.match_info["command"]

        # unique requestID for this command
        requestId = str(uuid.uuid1())

        payload = {
            "body": {
                # "origin": {"type": "player"},
                "commandLine": command,
                "version": 1,
            },
            "header": {
                "requestId": requestId,
                "messagePurpose": "commandRequest",
                "version": 1,
                "messageType": "commandRequest",
            },
        }

        with self.publisher.subscription() as queue:
            await self.recv_queue.put(json.dumps(payload))

            TIMEOUT = 5
            try:
                while True:
                    # check timeout
                    if time.time() - start_time > TIMEOUT:
                        raise asyncio.TimeoutError

                    # get from queue with timeout
                    response_raw: str = await asyncio.wait_for(
                        queue.get(), timeout=TIMEOUT
                    )
                    response = json.loads(response_raw)

                    if response["header"]["requestId"] == requestId:
                        break
            except asyncio.TimeoutError:
                log.debug("Timeout error...")
                response = {"error": "No response received."}

        time_taken = time.time() - start_time
        log.debug(f"Processed request in {time_taken:.2f}s.")
        return web.Response(
            text=json.dumps(response), headers={"Content-Type": "application/json"}
        )

    def start(self, loop: asyncio.BaseEventLoop):
        app = web.Application()
        app.add_routes([web.get("/{command}", lambda r: self.handler(r))])

        runner = web.AppRunner(app)
        loop.run_until_complete(runner.setup())
        self.site = web.TCPSite(runner, self.host, self.port)

        loop.run_until_complete(self.site.start())

        log.info(f"Serving HTTP bridge on port {self.port}")
