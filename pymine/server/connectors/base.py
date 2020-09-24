from abc import ABC, abstractmethod
import asyncio


class Connector(ABC):
    @abstractmethod
    def __init__(
        self, send_queue: asyncio.Queue, recv_queue: asyncio.Queue, *args, **kwargs
    ):
        raise NotImplementedError

    @abstractmethod
    def start(self, loop: asyncio.BaseEventLoop):
        raise NotImplementedError
