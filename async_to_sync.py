from threading import Thread, Event
import time


class AsyncExecutor:
    def work(self, callback):
        time.sleep(5)
        callback()

    def execute_async(self, callback):
        Thread(target=self.work, args=(callback,)).start()


def execute_sync(callback):
    event = Event()

    def wrapped_callback():
        callback()
        event.set()

    exec = AsyncExecutor()
    exec.execute_async(wrapped_callback)
    event.wait()


def say_hi():
    print("Hi")


if __name__ == "__main__":
    execute_sync(say_hi)

    print("main thread exiting")
