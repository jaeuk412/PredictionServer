import random
import asyncio
import websockets

from time import sleep

async def SendMsg(websocket, path, done_message):
    # for x in range(0,10):
    #     rand_number = random.randint(1, 1000)
    #     sleep(0.5)
    #     await websocket.send(str(rand_number))
    await websocket.send(str(done_message))


async def main(websocket, path):
    print(websocket)
    print(path)
    name = await websocket.recv()
    print(name)
    Send_ = asyncio.ensure_future((SendMsg(websocket,path, {"data":2})))
    print("Main Asyncio Start")
    asyncio.as_completed(Send_)


start_server = websockets.serve(main, "localhost", 8765)
loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
loop.run_forever()

# ssocket_start()