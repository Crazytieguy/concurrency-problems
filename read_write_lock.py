import random
import threading
import time
from dataclasses import dataclass
from threading import Condition, Lock, Thread

START = time.time()

PRINTING_LOCK = Lock()


def log(message: str):
    thread_name = threading.current_thread().name
    now = time.time() - START
    with PRINTING_LOCK:
        print(f"{now:.3f} {thread_name}: {message}")


class ReadWriteLock:
    _condition: Condition
    _readers: int
    _writers_waiting: int

    def __init__(self):
        self._condition = Condition()
        self._readers = 0
        self._writers_waiting = 0

    def acquire_read(self):
        with self._condition:
            self._condition.wait_for(lambda: self._writers_waiting == 0)
            self._readers += 1

    def release_read(self):
        with self._condition:
            if self._readers == 0:
                raise ValueError("Must acquire lock before releasing it")
            self._readers -= 1
            self._condition.notify_all()

    def acquire_write(self):
        self._condition.acquire()
        self._writers_waiting += 1
        self._condition.wait_for(lambda: self._readers == 0)
        self._writers_waiting -= 1

    def release_write(self):
        self._condition.notify_all()
        self._condition.release()


@dataclass
class Counter:
    value: int = 0

    def inc(self):
        self.value += 1


def reader(rw_lock: ReadWriteLock, counter: Counter):
    for _ in range(20):
        rw_lock.acquire_read()
        before_sleep = counter.value
        time.sleep(random.random())
        after_sleep = counter.value
        log(f"{before_sleep=}, {after_sleep=}")
        rw_lock.release_read()


def writer(rw_lock: ReadWriteLock, counter: Counter):
    for _ in range(5):
        time.sleep(random.random() * 3)
        rw_lock.acquire_write()
        log("incrementing")
        counter.inc()
        rw_lock.release_write()


def main():
    rw_lock = ReadWriteLock()
    counter = Counter()

    threads = [
        Thread(target=writer, name=f"Writer-{i}", args=(rw_lock, counter))
        for i in range(3)
    ] + [
        Thread(target=reader, name=f"Reader-{i}", args=(rw_lock, counter))
        for i in range(3)
    ]
    for t in threads:
        t.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
