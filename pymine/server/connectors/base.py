from abc import ABC, abstractmethod
import asyncio

from typing import Type


class Connector(ABC):
    @abstractmethod
    def __init__(
        self, send_queue: asyncio.Queue, recv_queue: asyncio.Queue, *args, **kwargs
    ):
        raise NotImplementedError

    @abstractmethod
    def start(self, loop: asyncio.BaseEventLoop):
        raise NotImplementedError


class Subscription:
    """
    Subscribes to a Publisher and returns the subscribe queue.
    """

    def __init__(self, publisher: Type[Publisher]):
        self.publisher = publisher
        self.queue = asyncio.Queue()

    def __enter__(self) -> asyncio.Queue:
        self.publisher.subscriptions.add(self.queue)
        return self.queue

    def __exit__(self, type, value, traceback):
        self.publisher.subscriptions.remove(self.queue)


class Publisher:
    def __init__(self):
        self.subscriptions = set()

    def publish(self, message: str):
        for queue in self.subscriptions:
            queue.put_nowait(message)

    def subscription(self) -> Type[Subscription]:
        sub = Subscription(self)
        return sub

