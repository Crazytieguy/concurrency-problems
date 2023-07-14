from __future__ import annotations

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


@dataclass
class Gender:
    _condition: Condition
    _name: str
    _queued: int = 0
    _entered: int = 0
    _finished: int = 0
    _other: Gender | None = None

    def enqueue(self):
        with self._condition:
            id_ = self._queued
            self._queued += 1
            log(f"{self._name} {id_} waiting")
            self._condition.wait_for(lambda: self._can_enter(id_))
            self._entered += 1
            log(f"{self._name} {id_} entering")

    def exit(self):
        with self._condition:
            self._finished += 1
            self._condition.notify_all()
            log(f"{self._name} exiting")

    def _can_enter(self, id_: int):
        if self._other is None:
            raise ValueError("Gender.other must be set")
        no_other_inside = self._other._entered == self._other._finished
        less_than_3_inside = self._finished + 3 > id_
        return no_other_inside and less_than_3_inside


class UnisexBathroom:
    males: Gender
    females: Gender

    def __init__(self):
        condition = Condition()
        self.males = Gender(condition, "male")
        self.females = Gender(condition, "female")
        self.males._other = self.females
        self.females._other = self.males


def person(gender: Gender):
    time.sleep(random.random() * 10)
    gender.enqueue()
    time.sleep(random.random() * 2)
    gender.exit()


def main():
    bathroom = UnisexBathroom()

    threads = [
        Thread(target=person, args=(bathroom.males,), name=f"Male-{i}")
        for i in range(10)
    ] + [
        Thread(target=person, args=(bathroom.females,), name=f"Female-{i}")
        for i in range(10)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
