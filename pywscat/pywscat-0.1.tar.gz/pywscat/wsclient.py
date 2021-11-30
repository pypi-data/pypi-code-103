#!/usr/bin/env python

# Simple python websocket client

import argparse
import websockets
import asyncio
from concurrent.futures import ThreadPoolExecutor

ws = None # Websocket

# Get input from stdin in a coroutine
async def ainput(prompt: str = ''):
    with ThreadPoolExecutor(1, 'ainput') as executor:
        return (await asyncio.get_event_loop().run_in_executor(executor, input, prompt)).rstrip()

# Function to listen for incoming messages not blocking
# args:
#   uri: websocket uri
#   callback: function to call when message is received
async def listen(uri, callback):
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            callback(message)

# Coroutine to start interactive send/recieve loop
# args:
#   uri: websocket uri
async def connect_and_print(uri):
    global ws

    async with websockets.connect(uri) as websocket:
        ws = websocket
        while True:
            print(await websocket.recv())


async def start(uri):
    global ws
    # Run connect_and_print coroutine as create_task
    asyncio.create_task(connect_and_print(uri))
    while True:
        if not ws:
            await asyncio.sleep(0.5)
            continue

        message = await ainput("")
        await ws.send(message)

def main():
    # Parse command line arguments
    # uri: websocket uri
    parser = argparse.ArgumentParser()
    parser.add_argument("uri", help="websocket uri")
    args = parser.parse_args()

    # Start interactive loop
    # asyncio.get_event_loop().run_until_complete(interactive(args.uri))
    asyncio.get_event_loop().run_until_complete(start(args.uri))

if __name__ == '__main__':
    main()