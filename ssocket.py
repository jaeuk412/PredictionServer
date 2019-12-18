import asyncio
import websockets
import datetime
import os
import json
from API.api_helper.user_directory import root_path
from async_timeout import timeout
from DB.DataBase.models import ResultTable
from DB.DataBase.database import db_session, dbsearch
from DB.DataBase.models import LocationTable, ModelTable
from API.api_helper.api_helper import devide_date
import time


async def SendMsg1(websocket, path, result):
    print('--------------22---------------')
    await websocket.send(json.dumps(result))

async def SendMsg2(websocket, path, result):
    await websocket.send(json.dumps(result))

def db_query(data):
    query = "SELECT model, location, start_date, user_key, temp_option, sub_option FROM result_save where key=%d" % (
        int(data))
    print(query)
    query_value = db_session.execute(query)





    value = []
    for y1 in query_value:

        for x, y in y1.items():
            value.extend([y])

    key_model = value[0]
    model_value = db_session.query(ModelTable).get(key_model)
    model_name = model_value.id

    key_area = value[1]
    location_value = db_session.query(LocationTable).get(key_area)
    area = location_value.id

    start_date = value[2]
    start_year, start_month, start_day = devide_date(start_date)
    user_key = value[3]
    temp_option = value[4]
    sub_option = value[5]

    print("model_name: ",model_name)
    print("area: ",area)

    datass = []
    from API.Predict.get_data_class import get_predic_data
    get_class = get_predic_data()

    print("model_name:", model_name)

    if model_name == 'daily':
        print("-------------------------")
        # datass = get_class.get_Daily_coming_30days_vaule(area, start_date, user_key)
        datass = get_class.get_Daily_coming_30days_vaule(area, 20191003, user_key)
    elif model_name == 'monthly1':
        # datass = get_class.get_Monthly_latest_12months_monthly_value(area, start_year - 1, start_month, temp_option, sub_option, user_key)
        datass = get_class.get_Monthly_latest_12months_monthly_value(area, 2018, 10,
                                                                     0, 0, user_key)
    elif model_name == 'monthly2':
        # datass = get_class.get_Monthly_coming_24months_monthly_value(area, start_year, start_month, user_key)
        datass = get_class.get_Monthly_coming_24months_monthly_value(area, 2019, 10,
                                                                     user_key)
    elif model_name == 'yearly':
        # datass = get_class.get_Yearly_coming_5years_month(area, start_year, user_key)
        datass = get_class.get_Yearly_coming_5years_month(area, 2019, user_key)

    return datass

'''
ws://localhost:10308/websocket
{"type":"predicted","data":{"id":1}}
'''

async def main(websocket, path):
    print('----websocket----')
    print(websocket)
    while True:
        try:
            ## 생성된 파일 있으면 웹으로 send.
            files = os.listdir(root_path + '/detectkey')
            # print("files: ",files)
            if files:
                for i in files:
                    try:
                        datass = db_query(i)
                        # result = {"data": {"dataset": i}}
                        result = {"type": "predicted", "dataset": {"id": int(i), "dataset": datass}}
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
            with timeout(0.01):
                name = await websocket.recv()

                print('----recv----')
                # jsonString = json.dumps(name)
                data = json.loads(name)
                print(data)
                print(type(data))

                if isinstance(data, dict):
                    data = data['dataset']
                    data = data['id']
                    print("id: ", data)

                    ## 데이터 쿼리.
                    datass = db_query(data)

                    # print(datass)
                    result = {"type": "predicted", "dataset": {"id": data, "dataset": datass}}
                    # print(result)
                    Send2 = asyncio.ensure_future((SendMsg2(websocket, path, result)))
                    asyncio.as_completed(Send2)
                    print("----send message----")

        except Exception as e:
            # print(websocket)
            ## 종료된 소켓은 disconnect.
            if str(type(e)) == "<class 'websockets.exceptions.ConnectionClosed'>":
                break
        # time.sleep(5)



# print("web-socket")
start_server = websockets.serve(main, "0.0.0.0", 10308)
loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
loop.run_forever()


