from threading import Condition, Lock, Thread
import random
import time
import threading

START = time.time()

PRINTING_LOCK = Lock()


def log(message: str):
    thread_name = threading.current_thread().name
    now = time.time() - START
    with PRINTING_LOCK:
        print(f"{now:.3f} {thread_name}: {message}")


class UnisexBathroom:
    _condition: Condition
    _males_queued: int
    _females_queued: int
    _males_entered: int
    _females_entered: int
    _males_finished: int
    _females_finished: int

    def __init__(self):
        self._condition = Condition()
        self._males_queued = 0
        self._females_queued = 0
        self._males_entered = 0
        self._females_entered = 0
        self._males_finished = 0
        self._females_finished = 0

    def enqueue_male(self):
        with self._condition:
            id_ = self._males_queued
            self._males_queued += 1
            log(f"male {id_} waiting")
            self._condition.wait_for(lambda: self._male_can_enter(id_))
            self._males_entered += 1
            log(f"male {id_} entering")

    def _male_can_enter(self, id_: int):
        no_females_inside = self._females_entered == self._females_finished
        less_than_3_males_inside = (self._males_finished + 3) > id_
        return no_females_inside and less_than_3_males_inside

    def male_finished(self):
        with self._condition:
            self._males_finished += 1
            self._condition.notify_all()
            log("male exiting")

    def enqueue_female(self):
        with self._condition:
            id_ = self._females_queued
            self._females_queued += 1
            log(f"female {id_} waiting")
            self._condition.wait_for(lambda: self._female_can_enter(id_))
            self._females_entered += 1
            log(f"female {id_} entering")

    def _female_can_enter(self, id_: int):
        no_males_inside = self._males_entered == self._males_finished
        less_than_3_females_inside = (self._females_finished + 3) > id_
        return no_males_inside and less_than_3_females_inside

    def female_finished(self):
        with self._condition:
            self._females_finished += 1
            self._condition.notify_all()
            log("female exiting")


def male(bathroom: UnisexBathroom):
    time.sleep(random.random() * 10)
    bathroom.enqueue_male()
    time.sleep(random.random() * 2)
    bathroom.male_finished()


def female(bathroom: UnisexBathroom):
    time.sleep(random.random() * 10)
    bathroom.enqueue_female()
    time.sleep(random.random() * 2)
    bathroom.female_finished()


def main():
    bathroom = UnisexBathroom()

    threads = [
        Thread(target=male, args=(bathroom,), name=f"Male-{i}") for i in range(10)
    ] + [Thread(target=female, args=(bathroom,), name=f"Female-{i}") for i in range(10)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
