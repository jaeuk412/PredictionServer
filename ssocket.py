import random
import asyncio
import websockets
import time
import os
from API.api_helper.user_directory import root_path
import json
from time import sleep

async def SendMsg1(websocket, path, name):
    # for x in range(0,10):
    #     rand_number = random.randint(1, 1000)
    #     sleep(0.5)
    #     await websocket.send(str(rand_number))
    print(websocket.recv())

    while True:

        try:
            files = os.listdir(root_path+'/detectkey')

            print(files)
            if files:
                for i in files:
                    # print(i)
                    # ivalue = i.split('_')
                    result = {"id":i}
                    await websocket.send(i)
                    try:
                        os.remove(root_path + '/detectkey/' + i)
                    except:
                        pass
        except:
            pass

        time.sleep(3)


async def SendMsg2(websocket, path, name):
    result = { "type":"predicted", "data":{"id":name,"dataset":"value"}}

    await websocket.send(json.dumps(result))

async def main(websocket, path):
    name = await websocket.recv()
    print(name)

    # Send_ = asyncio.ensure_future((SendMsg2(websocket, path, name)))
    Send_ = asyncio.ensure_future((SendMsg1(websocket, path, name)))

    asyncio.as_completed(Send_)
    # asyncio.as_completed(Send1_)
    print("Main Asyncio Start")

    # asyncio.as_completed(Send1_)

start_server = websockets.serve(main, "0.0.0.0",8888)
loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
loop.run_forever()

# ssocket_start()

