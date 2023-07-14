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
    barrier: Barrier
    lock: Lock
    driver_chosen: bool
    passengers: list[str]

    def __init__(self):
        self.barrier = Barrier(4)
        self.lock = Lock()
        self.driver_chosen = False
        self.passengers = []

    def drive(self):
        log(f"driving {self.passengers}")

    def take_seat(self) -> bool:
        self.passengers.append(threading.current_thread().name)
        log("seated")
        self.barrier.wait()
        with self.lock:
            if self.driver_chosen:
                return False
            else:
                self.driver_chosen = True
                return True


class Uber:
    democrats: deque[Queue]
    republicans: deque[Queue]
    lock: Lock

    def __init__(self):
        self.democrats = deque()
        self.republicans = deque()
        self.lock = Lock()

    def order_uber_democrat(self) -> Ride:
        log("waiting")
        queue = Queue(1)
        with self.lock:
            self.democrats.append(queue)
            self.try_find_ride()
        return queue.get()

    def order_uber_republican(self) -> Ride:
        log("waiting")
        queue = Queue(1)
        with self.lock:
            self.republicans.append(queue)
            self.try_find_ride()
        return queue.get()

    def try_find_ride(self):
        if len(self.democrats) >= 2 and len(self.republicans) >= 2:
            ride = Ride()
            for _ in range(2):
                self.democrats.popleft().put(ride)
            for _ in range(2):
                self.republicans.popleft().put(ride)
            return
        if len(self.democrats) >= 4:
            ride = Ride()
            for _ in range(4):
                self.democrats.popleft().put(ride)
            return
        if len(self.republicans) >= 4:
            ride = Ride()
            for _ in range(4):
                self.republicans.popleft().put(ride)
            return


def democrat(uber: Uber):
    time.sleep(random.random() * 10)
    ride = uber.order_uber_democrat()
    if ride.take_seat():
        ride.drive()


def republican(uber: Uber):
    time.sleep(random.random() * 10)
    ride = uber.order_uber_republican()
    time.sleep(random.random())
    if ride.take_seat():
        ride.drive()


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
