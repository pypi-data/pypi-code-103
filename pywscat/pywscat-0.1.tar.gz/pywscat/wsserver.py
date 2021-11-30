#!/usr/bin/env python

import websockets
import asyncio
from concurrent.futures import ThreadPoolExecutor


# Websocket server

num_connections = 0
wslist = [] # List of connected clients
websocket_host = "0.0.0.0"
websocket_port = 8888

# Get input from stdin in a coroutine
async def ainput(prompt: str = ''):
    with ThreadPoolExecutor(1, 'ainput') as executor:
        return (await asyncio.get_event_loop().run_in_executor(executor, input, prompt)).rstrip()


async def send_all(message):
    global wslist
    for ws in wslist:
        await ws.send(message)

async def handle(websocket):
    global wslist

    # Add client to list of connected clients
    wslist.append(websocket)

    # Print connected client ip address
    print("Client connected: " + websocket.remote_address[0])

    # Send hello message to client
    await websocket.send("Hello!")

    try:
        while True:
            message = await websocket.recv()
            print(message)
            await send_all(message)
    except Exception as e:
        #print(e)
        print("Client disconnected: " + websocket.remote_address[0])

    # Remove client from list of connected clients
    wslist.remove(websocket)

async def terminal_loop():
        
    while True:
        message = await ainput("Enter message: ")
        if message == "quit":
            break
        await send_all(message)

def main():
    # Start the websocket server
    start_server = websockets.serve(handle, websocket_host, websocket_port)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_until_complete(terminal_loop())
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()