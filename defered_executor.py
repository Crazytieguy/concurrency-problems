import threading
import time
from queue import Empty, PriorityQueue, Queue
from threading import Thread

START = time.time()


def log(message: str):
    thread_name = threading.current_thread().name
    now = time.time() - START
    print(f"{now:.3f} {thread_name}: {message}")


class DeferedExecutor:
    _queue: Queue
    _executor_thread: Thread

    def __init__(self):
        self._queue = Queue()
        self._executor_thread = Thread(target=self._executor, daemon=True)
        self._executor_thread.start()

    def _executor(self):
        tasks = PriorityQueue()
        while True:
            try:
                (execute_at, callback, args, kwargs) = tasks.get_nowait()
                timeout = execute_at - time.time()
                try:
                    new_item = self._queue.get(timeout=timeout)
                    tasks.put(new_item)
                    tasks.put((execute_at, callback, args, kwargs))
                except Empty:
                    callback(*args, **kwargs)
            except Empty:
                item = self._queue.get()
                tasks.put(item)

    def defer(self, callback, delay, *args, **kwargs):
        execute_at = time.time() + delay
        self._queue.put((execute_at, callback, args, kwargs))


def main():
    executor = DeferedExecutor()

    executor.defer(log, 4, "four")
    executor.defer(log, 2, "two")
    executor.defer(log, 3, "three")
    executor.defer(log, 1, "one")

    time.sleep(5)


if __name__ == "__main__":
    main()
