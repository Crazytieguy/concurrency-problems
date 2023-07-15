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
class Philosopher:
    condition: Condition
    forks: tuple[Lock, Lock]

    def run(self):
        for _ in range(5):
            self.contemplate()
            self.eat()

    def contemplate(self):
        log("contemplating")
        time.sleep(random.random() * 3)

    def eat(self):
        log("attempting to eat")
        with self.condition:
            self.condition.wait_for(self._try_pick_up_forks)

        log("eating")
        time.sleep(random.random() * 5)

        with self.condition:
            self.forks[0].release()
            self.forks[1].release()
            self.condition.notify_all()

    def _try_pick_up_forks(self) -> bool:
        if self.forks[0].acquire(blocking=False):
            if self.forks[1].acquire(blocking=False):
                return True
            self.forks[0].release()
        return False


def make_philosopher_table() -> list[Philosopher]:
    forks = [Lock() for _ in range(5)]
    condition = Condition()

    return [Philosopher(condition, (forks[i - 1], forks[i])) for i in range(5)]


def main():
    philosophers = make_philosopher_table()

    threads = [
        Thread(target=p.run, name=f"Philosopher-{i}")
        for i, p in enumerate(philosophers)
    ]

    for t in threads:
        t.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
