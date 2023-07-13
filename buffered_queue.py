import logging
from collections import deque
from random import random
from threading import Semaphore, Thread, current_thread
from time import sleep
from typing import Any

FORMAT = "%(asctime)s.%(msecs)03d %(threadName)s: %(message)s"
logging.basicConfig(format=FORMAT, datefmt="%H:%M:%S")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Queue:
    _data: deque
    _get_semaphore: Semaphore
    _put_semaphore: Semaphore

    def __init__(self, max_size: int = 2):
        self._data = deque()
        self._get_semaphore = Semaphore(0)
        self._put_semaphore = Semaphore(max_size)

    def put(self, item: Any, blocking: bool = True) -> bool:
        """
        Put an item into the queue, returning whether the operation was successful.
        If `blocking` is `True` (the default), waits until there's room in the queue.
        If `blocking` is `False` and there isn't room, returns False immediately.

        Note: Putting `None` on the queue is illegal,
        as None is used to signal a failed non-blocking get()
        """
        if item is None:
            raise ValueError(
                "Can't put None, as it is used to signal a failed non-blocking get()"
            )
        if self._put_semaphore.acquire(blocking=blocking):
            self._data.append(item)
            self._get_semaphore.release()
            return True
        return False

    def get(self, blocking: bool = True) -> Any:
        if self._get_semaphore.acquire(blocking=blocking):
            ret = self._data.popleft()
            self._put_semaphore.release()
            return ret
        return None


CONSUMER_MAX_SLEEP = 4
PRODUCER_MAX_SLEEP = 2


def consumer(queue: Queue):
    while True:
        sleep(random() * CONSUMER_MAX_SLEEP)
        item = queue.get()
        logger.info(f"got {item}")


def producer(queue: Queue):
    for i in range(5):
        sleep(random() * PRODUCER_MAX_SLEEP)
        item = f"{current_thread().name}:{i}"
        queue.put(item)
        logger.info(f"put {item}")


def main():
    queue = Queue()

    for i in range(2):
        Thread(
            target=consumer, name=f"Consumer-{i}", args=(queue,), daemon=True
        ).start()

    producers = [
        Thread(target=producer, name=f"Producer-{i}", args=(queue,)) for i in range(2)
    ]
    for thread in producers:
        thread.start()

    for i in range(5):
        sleep(random() * PRODUCER_MAX_SLEEP)
        logger.info("try put")
        success = queue.put(f"M{i}", blocking=False)
        logger.info("success!" if success else "no luck")

        sleep(random() * CONSUMER_MAX_SLEEP)
        logger.info("try get")
        item = queue.get(blocking=False)
        logger.info(f"got {item}" if item is not None else "no luck")

    for thread in producers:
        thread.join()

    sleep(CONSUMER_MAX_SLEEP)


if __name__ == "__main__":
    main()
