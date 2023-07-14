import random
import threading
import time
from collections import deque
from threading import Event, Lock, Thread

START = time.time()

PRINTING_LOCK = Lock()


def log(message: str):
    thread_name = threading.current_thread().name
    now = time.time() - START
    with PRINTING_LOCK:
        print(f"{now:.3f} {thread_name}: {message}")


class Uber:
    democrats: deque[Event]
    republicans: deque[Event]
    lock: Lock

    def __init__(self):
        self.democrats = deque()
        self.republicans = deque()
        self.lock = Lock()

    def order_uber_democrat(self):
        log("democrat waiting")
        event = Event()
        with self.lock:
            self.democrats.append(event)
            self.try_find_ride()
        event.wait()
        log("democrat seated")

    def order_uber_republican(self):
        log("replublican waiting")
        event = Event()
        with self.lock:
            self.republicans.append(event)
            self.try_find_ride()
        event.wait()
        log("replublican seated")

    def try_find_ride(self):
        if len(self.democrats) >= 2 and len(self.republicans) >= 2:
            for _ in range(2):
                self.democrats.popleft().set()
            for _ in range(2):
                self.republicans.popleft().set()
            return
        if len(self.democrats) >= 4:
            for _ in range(4):
                self.democrats.popleft().set()
            return
        if len(self.republicans) >= 4:
            for _ in range(4):
                self.republicans.popleft().set()
            return


def random_delay(callback):
    def inner():
        time.sleep(random.random() * 10)
        callback()

    return inner


def main():
    uber = Uber()

    threads = [
        Thread(target=random_delay(uber.order_uber_democrat)) for _ in range(10)
    ] + [Thread(target=random_delay(uber.order_uber_republican)) for _ in range(10)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
