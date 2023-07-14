import random
import threading
import time
from threading import BoundedSemaphore, Thread

START = time.time()


def set_start():
    global START
    START = time.time()


def log(message: str):
    thread_name = threading.current_thread().name
    now = time.time() - START
    print(f"{now:.3f} {thread_name}: {message}")


class TockenBucket:
    _semaphore: BoundedSemaphore
    _filler_thread: Thread

    def __init__(self, max_tockens: int = 10):
        self._semaphore = BoundedSemaphore(max_tockens)
        self._filler_thread = Thread(
            target=self._fill_bucket, name="Filler", daemon=True
        )
        self._filler_thread.start()

    def _fill_bucket(self):
        while True:
            try:
                self._semaphore.release()
            except ValueError:
                log("Bucket full")
                pass
            time.sleep(0.5)

    def get_tocken(self):
        self._semaphore.acquire()
        log(f"{self._semaphore._value} tockens remaining")


def consumer(bucket: TockenBucket):
    for _ in range(10):
        time.sleep(random.random())
        bucket.get_tocken()


def consumer_thread(i: int, bucket: TockenBucket):
    return Thread(target=consumer, name=f"Consumer-{i}", args=(bucket,))


def main():
    set_start()
    
    bucket = TockenBucket()

    threads = [consumer_thread(i, bucket) for i in range(4)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    time.sleep(10)

    threads = [consumer_thread(i, bucket) for i in range(4)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
