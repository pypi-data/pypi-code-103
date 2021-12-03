# async programming
import asyncio
import time

start = time.time()

async def main():
    task = asyncio.create_task(other())
    print("A")
    print("B")

async def other():
    print("1")
    await asyncio.sleep(2)
    print("2")


asyncio.run(main())
print(f"It took {round(time.time()-start,2)} second(s)")