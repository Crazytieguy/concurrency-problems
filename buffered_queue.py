from threading import Semaphore, current_thread, Thread
from typing import Any
from collections import deque
from itertools import count
from time import sleep
from random import random


class Queue:
    _data: deque
    _get_semaphore: Semaphore
    _put_semaphore: Semaphore

    def __init__(self, max_size: int = 3):
        self._data = deque()
        self._get_semaphore = Semaphore(0)
        self._put_semaphore = Semaphore(max_size)

    def put(self, item: Any):
        self._put_semaphore.acquire()
        self._data.append(item)
        self._get_semaphore.release()

    def get(self) -> Any:
        self._get_semaphore.acquire()
        ret = self._data.popleft()
        self._put_semaphore.release()
        return ret


CONSUMER_MAX_SLEEP = 5
PRODUCER_MAX_SLEEP = 2


def consumer(queue: Queue):
    while True:
        sleep(random() * CONSUMER_MAX_SLEEP)
        item = queue.get()
        print(f"{current_thread().name} got {item}")


def producer(queue: Queue):
    for i in count():
        sleep(random() * PRODUCER_MAX_SLEEP)
        item = f"{current_thread().name}:{i}"
        queue.put(item)
        print(f"{current_thread().name} put {item}")


def main():
    queue = Queue()

    for i in range(3):
        Thread(target=consumer, name=f"C{i}", args=(queue,), daemon=True).start()

    for i in range(2):
        Thread(target=producer, name=f"P{i}", args=(queue,), daemon=True).start()

    sleep(60)


if __name__ == "__main__":
    main()
