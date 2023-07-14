import random
import threading
import time
from collections import deque
from queue import Queue
from threading import Barrier, Lock, Thread

START = time.time()

PRINTING_LOCK = Lock()


def log(message: str):
    thread_name = threading.current_thread().name
    now = time.time() - START
    with PRINTING_LOCK:
        print(f"{now:.3f} {thread_name}: {message}")


class Ride:
    _barrier: Barrier
    _passengers: list[str]

    def __init__(self):
        self._barrier = Barrier(4)
        self._lock = Lock()
        self._driver_chosen = False
        self._passengers = []

    def _drive(self):
        log(f"driving {self._passengers}")

    def take_seat(self):
        name = threading.current_thread().name
        self._passengers.append(name)
        log("seated")
        self._barrier.wait()
        if name == self._passengers[0]:
            self._drive()


class Uber:
    _democrats: deque[Queue]
    _republicans: deque[Queue]
    _lock: Lock

    def __init__(self):
        self._democrats = deque()
        self._republicans = deque()
        self._lock = Lock()

    def order_uber_democrat(self) -> Ride:
        log("waiting")
        queue = Queue(1)
        with self._lock:
            self._democrats.append(queue)
            self._try_find_ride()
        return queue.get()

    def order_uber_republican(self) -> Ride:
        log("waiting")
        queue = Queue(1)
        with self._lock:
            self._republicans.append(queue)
            self._try_find_ride()
        return queue.get()

    def _try_find_ride(self):
        if len(self._democrats) >= 2 and len(self._republicans) >= 2:
            ride = Ride()
            for _ in range(2):
                self._democrats.popleft().put(ride)
            for _ in range(2):
                self._republicans.popleft().put(ride)
            return
        if len(self._democrats) >= 4:
            ride = Ride()
            for _ in range(4):
                self._democrats.popleft().put(ride)
            return
        if len(self._republicans) >= 4:
            ride = Ride()
            for _ in range(4):
                self._republicans.popleft().put(ride)
            return


def democrat(uber: Uber):
    time.sleep(random.random() * 10)
    ride = uber.order_uber_democrat()
    time.sleep(random.random())
    ride.take_seat()


def republican(uber: Uber):
    time.sleep(random.random() * 10)
    ride = uber.order_uber_republican()
    time.sleep(random.random())
    ride.take_seat()


def main():
    uber = Uber()

    threads = [
        Thread(target=democrat, args=(uber,), name=f"Democ-{i}") for i in range(10)
    ] + [Thread(target=republican, args=(uber,), name=f"Repub-{i}") for i in range(10)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
