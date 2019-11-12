
import asyncio
import websockets
import os
import json
from API.api_helper.user_directory import root_path
from async_timeout import timeout
from DB.DataBase.models import ResultTable
from DB.DataBase.database import db_session, dbsearch
from API.api_helper.api_helper import devide_date


async def SendMsg1(websocket, path, result):
    print('--------------22---------------')
    await websocket.send(json.dumps(result))

async def SendMsg2(websocket, path, result):
    await websocket.send(json.dumps(result))

'''
ws://localhost:10308/websocket
{"type":"predicted","data":{"id":"daily"}}
'''

async def main(websocket, path):
    print('----websocket----')
    print(websocket)
    while True:
        try:
            ## 생성된 파일 있으면 웹으로 send.
            files = os.listdir(root_path + '/detectkey')
            if files:
                for i in files:
                    try:
                        result = {"data": {"dataset": i}}
                        Send1 = asyncio.ensure_future((SendMsg2(websocket, path, result)))
                        asyncio.as_completed(Send1)
                        ## send된 파일 제거.
                        os.remove(root_path + '/detectkey/' + i)
                    except:
                        pass

            # if count == 0:
            #     websocket.recv()
            # else:
            # 웹으로부터 recv.
            with timeout(1):
                name = await websocket.recv()

                print('----recv----')
                # jsonString = json.dumps(name)
                data = json.loads(name)
                print(data)

                if isinstance(data, dict):
                    data = data['data']
                    data = data['id']
                    print("id: ", data)


                    print(type(data))

                    ## todo: ResultTable DB의 pkey 에 해당하는 내용 push
                    query = "SELECT model_name, location, start_date, user_pkey, temp_option, sub_option FROM result_save where pkey=%d"%(int(data))
                    query_value = db_session.execute(query)

                    print(query)

                    # save_monthly
                    model_name = str()

                    value = []
                    for y1 in query_value:

                        for x, y in y1.items():
                            value.extend([y])


                    print(value)
                    print(type(value))

                    model_name = value[0]

                    area = value[1]
                    start_date = value[2]
                    user_pkey = value[3]
                    start_year, start_month, start_day = devide_date(start_date)
                    temp_option = value[4]
                    sub_option = value[5]


                    datass = []
                    from API.Predict.get_data_class import get_predic_data
                    get_class = get_predic_data()

                    print("model_name:",model_name)

                    if model_name == 'daily':
                        print("-------------------------")
                        datass = get_class.get_Daily_coming_30days_vaule(area, start_date, user_pkey)
                    elif model_name =='monthly1':
                        datass = get_class.get_Monthly_latest_12months_monthly_value(area, start_year - 1, start_month, temp_option, sub_option, user_pkey)
                    elif model_name == 'monthly2':
                        datass = get_class.get_Monthly_coming_24months_monthly_value(area, start_year, start_month, user_pkey)
                    elif model_name == 'yearly':
                        datass = get_class.get_Yearly_coming_5years_month(area, start_year, user_pkey)
                    # print(datass)
                    result = {"type": "predicted", "data": {"id": data, "dataset": datass}}
                    # print(result)
                    Send2 = asyncio.ensure_future((SendMsg2(websocket, path, result)))
                    asyncio.as_completed(Send2)
                    print("----send message----")

        except Exception as e:
            ## 종료된 소켓은 disconnect.
            if str(type(e)) == "<class 'websockets.exceptions.ConnectionClosed'>":
                break

start_server = websockets.serve(main, "0.0.0.0", 10308)
loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
loop.run_forever()


