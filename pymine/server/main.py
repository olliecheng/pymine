#!/usr/bin/env python3

import uuid
import json
import asyncio

from typing import List, Dict, Tuple, Sequence

from pymine.server.connectors.minecraft import MinecraftConnector


def start_server(port: int = 19131):
    print(f"Starting server on port {port}")

    send_queue = asyncio.Queue()
    recv_queue = asyncio.Queue()

    minecraft_connection = MinecraftConnector(
        send_queue, recv_queue, port=19131
    )

    event_loop = asyncio.get_event_loop()
    try:
        minecraft_connection.run_until_complete(event_loop)
        event_loop.run_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    start_server()
