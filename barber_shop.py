import asyncio
import random
import time
from asyncio import Event, Queue, QueueFull

START = time.time()


def log(name: str, message: str):
    now = time.time() - START
    print(f"{now:.3f} {name}: {message}")


class BarberShop:
    queue: Queue[Event]

    def __init__(self):
        self.queue = Queue(5)

    async def get_haircut(self, name: str):
        event = Event()
        try:
            self.queue.put_nowait(event)
        except QueueFull:
            log(name, "Room full, leaving")
            return False
        log(name, "Waiting for haircut")
        await event.wait()
        log(name, "Got haircut")

    async def run_barber(self):
        while True:
            customer = await self.queue.get()
            log("barber", "Giving haircut")
            await asyncio.sleep(1)
            customer.set()


async def customer(barber_shop: BarberShop, name: str):
    await asyncio.sleep(random.random() * 10)
    await barber_shop.get_haircut(name)


async def main():
    barber_shop = BarberShop()
    asyncio.create_task(barber_shop.run_barber())
    await asyncio.gather(*[customer(barber_shop, f"Cust-{i}") for i in range(20)])


if __name__ == "__main__":
    asyncio.run(main())
