import asyncio
import websockets
import datetime
import os
import json
from async_timeout import timeout
from DB.DataBase.models import ResultTable
from DB.DataBase.database import db_session, dbsearch
from DB.DataBase.models import LocationTable, ModelTable
from API.api_helper.api_helper import devide_date
from API.api_helper.user_directory import folder_detectkey_path
import time


async def SendMsg1(websocket, path, result):
    print('--------------22---------------')
    await websocket.send(json.dumps(result))

async def SendMsg2(websocket, path, result):
    await websocket.send(json.dumps(result))

def key_time(key):
    query = "SELECT inserted FROM result_save where key=%d" % (int(key))
    records = db_session.execute(query)

    for i in records:
        for x, y in i.items():
            insert_time = y

    from datetime import timedelta, datetime
    finished = datetime.now()
    ## 종료-시작 ( 종료가 안됐다면 None값)
    exe_time = (finished - insert_time).seconds
    # print(finished)
    # print(insert_time)
    # print('-------------------------')

    return exe_time


def db_query(data):
    query = "SELECT model, location, start_date, user_key, temp_option, sub_option FROM result_save where key=%d" % (
        int(data))
    # print(query)
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
    print("user_key: ",user_key)

    datass = []
    from API.Predict.get_data_class import get_predic_data
    get_class = get_predic_data()


    if model_name == 'daily':
        # print("-------------------------")
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
    count = 0
    while True:
        try:
            ## 생성된 파일 있으면 웹으로 send.
            files = os.listdir(folder_detectkey_path)
            # print("files: ",files)
            if files:

                time_result = {}
                for i in files:
                    if 'DONE' in i:
                        try:
                            queryi = i.split('_')[1]
                            datass = db_query(queryi)
                            # result = {"data": {"dataset": i}}
                            result = {"type": "predicted", "dataset": {"id": int(queryi), "dataset": datass}}
                            Send1 = asyncio.ensure_future((SendMsg2(websocket, path, result)))
                            asyncio.as_completed(Send1)
                            ## send된 파일 제거.
                            os.remove(folder_detectkey_path + i)
                        except:
                            pass
                    elif "ING" in i:
                        try:

                            key = i.split('_')[1]
                            exe_time = key_time(key)
                            each_time_value = {int(key): exe_time}
                            time_result.update(each_time_value)

                        except:
                            time_result = {}

                if time_result:
                    if count > 600:
                        final_time_result = {"type": "process", "dataset": time_result}
                        Send2 = asyncio.ensure_future((SendMsg2(websocket, path, final_time_result)))
                        asyncio.as_completed(Send2)
                        count = 0
                    count += 1


            # if count == 0:
            #     websocket.recv()
            # else:
            # 웹으로부터 recv.
            with timeout(0.01):
                name = await websocket.recv()

                print('----recv----')
                # jsonString = json.dumps(name)
                data = json.loads(name)
                # print(data)
                # print(type(data))

                if isinstance(data, dict):
                    data = data['dataset']
                    data = data['id']
                    # print("id: ", data)

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


