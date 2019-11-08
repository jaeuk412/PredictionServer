import random
import asyncio
import websockets
import time
import os
from API.api_helper.user_directory import root_path
from time import sleep

async def SendMsg(websocket, path):
    # for x in range(0,10):
    #     rand_number = random.randint(1, 1000)
    #     sleep(0.5)
    #     await websocket.send(str(rand_number))
    while(1):
        try:
            files = os.listdir(root_path+'/detectkey')
            print(files)
            if files:
                for i in files:
                    print(i)
                    await websocket.send(i)
                    try:
                        os.remove(root_path + '/detectkey/' + i)
                    except:
                        pass
        except:
            pass


        time.sleep(3)

async def main(websocket, path):
    name = await websocket.recv()
    print(name)
    Send_ = asyncio.ensure_future((SendMsg(websocket, path)))
    asyncio.as_completed(Send_)
    print("Main Asyncio Start")

    # asyncio.as_completed(Send1_)


def ssocket_start():
    start_server = websockets.serve(main, "localhost",8888)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    loop.run_forever()

ssocket_start()