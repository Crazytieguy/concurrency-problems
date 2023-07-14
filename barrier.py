import random
import threading
import time
from threading import Condition, Lock, Thread

START = time.time()

PRINTING_LOCK = Lock()


def log(message: str):
    thread_name = threading.current_thread().name
    now = time.time() - START
    with PRINTING_LOCK:
        print(f"{now:.3f} {thread_name}: {message}")


class Barrier:
    _target: int
    _waiting: int
    _condition: Condition

    def __init__(self, target: int):
        self._target = target
        self._waiting = 0
        self._condition = Condition()

    def wait(self):
        with self._condition:
            self._waiting += 1
            self._condition.notify_all()
            log(f"waiting: {self._waiting}")
            self._condition.wait_for(lambda: self._waiting == self._target)
            log("done waiting")


def sleep_then_wait(barrier: Barrier):
    time.sleep(random.random() * 5)
    barrier.wait()


def main():
    barrier = Barrier(5)

    threads = [Thread(target=sleep_then_wait, args=(barrier,)) for _ in range(5)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
