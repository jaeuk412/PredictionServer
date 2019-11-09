# -*- coding: utf-8 -*-
# predic_dedail set API

'''general'''
import json
import datetime
import os
import time
import random
import string
'''library'''
## flask(REST-API)
from flask import Blueprint, jsonify, send_from_directory, abort, session, send_file
from flask import make_response, request, current_app, Response
##  check format of data
import wtforms_json
from wtforms import Form, StringField, IntegerField
from wtforms.validators import InputRequired

import requests
import pandas as pd
# ## schedule
# from apscheduler.schedulers.background import BackgroundScheduler, BlockingScheduler
# sched = BackgroundScheduler()
# ##
from threading import Thread
import multiprocessing
from urllib.request import urlopen
# ##
# import subprocess
# ##
# import asyncio
'''directory'''
## database
from DB.DataBase.database import db_session
from DB.DataBase.models import DailyTable, MonthlyTable1, MonthlyTable2, YearlyTable, Login
from DB.DataBase.database import dbsearch
## api helper
from API.api_helper.api_helper import crossdomain, get_query_string, get_query_key, file_remove, devide_date, get_user_pkey
from API.api_helper.api_helper import post_request, response_json_list, response_json_value, date_time
from API.api_helper.user_directory import folder_path
from API.Predict.set_data_class import set_predic_data
from API.Predict.get_data_class import get_predic_data, get_train_model
from flask_sse import sse
from socket import *
import websockets
''' '''
from flask_cors import CORS

predic_apis = Blueprint('predic_d_set_apis', __name__, url_prefix='/api')

wtforms_json.init()



## ---------------------------------------------------------------------------------
## predic_daily set
## area, start_year, start_month, start_day
## executation
## 실행 2분.

## 밑에 3줄만 backtasks로 해서 웹으로 통신.
    ## 웹 정보를 얻으려면, 처음 backtastk 실행 시켰던 정보(request.headers) ip를 받아서, connect해서 전송.
@predic_apis.route('/hello')
def publish_hello():
    sse.publish({"message": "Hello!"}, type='greeting')
    return "Message sent!"

@predic_apis.route('/infer/predict/daily', methods=['POST'])
def api_predict_daily_set():
    pkey = get_user_pkey

    try:
        req = request.get_json()
        jsonString = json.dumps(req)
        data = json.loads(jsonString)

        sort = data['sort']
        area = data['area']
        model = data['model'] # DB 저장용.
        start_date = data['start_date']

    except:
        abort(400)

    else:
        # print("start_date: ",start_date)

        dt = datetime.datetime.now()

        if not start_date:
            start_date, start_year, start_month, start_day = date_time(dt)
            # 오전 7시에 예보데이터 나옴.
            if dt.hour <= 7:
                start_day = start_day - 1
        else:
            start_year, start_month, start_day = devide_date(start_date)



        ## 만약 기존 DB에 날짜 and insu and 지역 이름 같으면 inserted 시간만 갱신.
        # try:

            #     return jsonify("already exist")
            # else:

        daily_output_file = folder_path + 'result/%s/predict_%s_%d_%d_%d_daily' % (pkey, area, start_year, start_month, start_day)

        db_session.add(DailyTable(resource=sort, location=area, model_name=model, start_date=start_date, end_date=start_date, save_path=daily_output_file))
        db_session.commit()

        detectkey = db_session.query(DailyTable.pkey).order_by(DailyTable.pkey.desc())
        print(detectkey[0][0])

        set_class = set_predic_data()
        set_class.set_Daily_coming_30days(area, start_year, start_month, start_day, detectkey[0][0])

        final_reuslt = {"id":detectkey[0][0]}
        return jsonify(final_reuslt)
        # except:
        #     return jsonify(False)

'''

# query = db_session.query(DailyTable.start_date).order_by(DailyTable.pkey.desc())
            # pkey = get_query_key(query)

            print("start_date: ", start_date)
            ## background 방식.
            # try:
            #     sched = BackgroundScheduler()
            #     sched.start()
            #     sched.add_job(execute_daily(area, start_year, start_month, start_day, pkey), id="test_1")
            # except KeyboardInterrupt:
            #     print("error")
            #
            # ## 비동기 방식.
            # loop = asyncio.new_event_loop()
            # asyncio.ensure_future(execute_daily(area, start_year, start_month, start_day, pkey))
            # loop.run_forever()

            # ## Thread
            # t = Thread(target = execute_daily(area, start_year, start_month, start_day, pkey), args=("Thread-1",180))
            # t.start()
            # t.join()

            # ## multiprocess
            # t = multiprocessing.Process(target= execute_daily(area, start_year, start_month, start_day, pkey), args=("Thread-1",180) )
            # t.start()
            # t.join()

            # from backtasks import daily
            # daily.delay(area, start_year, start_month, start_day)
'''






## 비동기 방식 함수 호출 실행.
# @asyncio.coroutine
# def execute_daily(area, start_year, start_month, start_day, pkey):
#     while True:
#         set_class = set_predic_data()
#         vv = set_class.set_Daily_coming_30days(area, start_year, start_month, start_day, pkey)
#         if vv == True:
#             break

# def execute_daily(area, start_year, start_month, start_day, pkey):
#     set_class = set_predic_data()
#     set_class.set_Daily_coming_30days(area, start_year, start_month, start_day, pkey)

## predic_daily get
@predic_apis.route('/infer/predict/daily', methods=['GET'])
def api_predict_daily_get_list():

    # query = db_session.query(DailyTable.pkey.label('ddawd')).order_by(DailyTable.pkey.desc())
    query = "select * from daily ORDER BY pkey desc"
    result = db_session.execute(query)

    # rows = result.fetchall()
    # print(rows)  # 전체 rows

    # for i in result:
    #     for x,y in i.items():
    #         print(x,y)

    # for i in result:
    #     print(i)
    #     print(i.keys())

    return response_json_list(result)

## predic_daily get
@predic_apis.route('/infer/predict/daily/<int:pkey>', methods=['GET'])
def api_predict_daily_get_item(pkey):

    # query = db_session.query(DailyTable).filter(DailyTable.pkey == pkey).order_by(DailyTable.pkey.desc())
    query = "select * from daily where pkey=%s"%(pkey)
    result = db_session.execute(query)

    return response_json_value(result)

## predic_daily delete
@predic_apis.route('/infer/predict/daily/<int:pkey>', methods=['DELETE'])
def api_predict_daily_get_delete(pkey):
    db = db_session.query(DailyTable).get(pkey)
    area = db.target_area
    start_date = db.start_date

    start_year, start_month, start_day = devide_date(start_date)
    path = folder_path + 'result/%s/predict_%s_%s_%s_%s_daily' % (
    start_date, area, start_year, start_month, start_day)

    try:
        db_session.query(DailyTable).filter(DailyTable.pkey == pkey).delete()
        db_session.commit()

        file_remove(path)
    except Exception as e:
        db_session.rollback()
        print(e)
        return jsonify(False)

    return jsonify(True)

## predic_daily get
@predic_apis.route('/infer/predict/daily/<int:pkey>/values', methods=['GET'])
def api_predict_daily_get_value(pkey):

    # TODO: 디비 정보로 area,yaer,month,day

    db = db_session.query(DailyTable).get(pkey)
    area = db.target_area
    start_date = db.start_date

    get_class = get_predic_data()
    value = get_class.get_Daily_coming_30days_vaule(area, start_date)
    if value == False:
        return 'have to test before this'

    return jsonify(value)

##############################################################################################
########################  Monthly-past12  ####################################################
##############################################################################################

## predic_monthly past12 set
## area, start_year, start_month, month_range, temp_mode, sub_mode
## 실행 20분 내외.
@predic_apis.route('/infer/predict/monthly1', methods=['POST'])
def api_predict_monthly_past12_set():
    try:
        req = request.get_json()
        jsonString = json.dumps(req)
        data = json.loads(jsonString)

        sort = data['sort']
        area = data['area']
        model = data['model']
        start_date = data['start_date']
        temp_mode = data['temp_option']
        sub_mode = data['sub_option']
    except:
        abort(400)
    else:
        if not start_date:
            dt = datetime.datetime.now()
            start_date, start_year, start_month, start_day = date_time(dt)
        else:
            start_year, start_month, start_day = devide_date(start_date)

        try:

            ''' 
            1. 요청날짜가 data/sub,insu(~2019.9보유중),temp(~2019.12보유중)데이터보다 이전 날짜를 만족해야 실행 됨.
            2. 요청한 날짜의 앞뒤로 1년 데이터로 뭐 하는거 같음
            3. 20190701로 하니까 20191001, 20191101 데이터(없는데이터)를 가져오려해서 Error 발생.
            3-2. past12는 과거 1년 날짜로 시작하는게 아닌가 하는 생각이 듬.
            3-3 20181005 날짜로 실행, (2018-10-01 ~ 2019-09-01) 데이터. okay. result/20191005/past~~ 저장.
            '''


            db_session.add(
                MonthlyTable1(target_sort=sort, target_area=area, model_name=model, start_date=start_date,
                              month_range=12, temp_option=temp_mode, sub_option=sub_mode))
            db_session.commit()

            detectkey = db_session.query(MonthlyTable1.pkey).order_by(MonthlyTable1.pkey.desc())
            print(detectkey[0][0])

            set_class = set_predic_data()
            set_class.set_Monthly_latest_12months(area, start_year - 1, start_month, 12, temp_mode, sub_mode,
                                                  start_date, detectkey[0][0])
            final_result = {"id":detectkey[0][0]}
            return jsonify(final_result)
        except:
            return jsonify(False)


## predic_monthly past12 get
@predic_apis.route('/infer/predict/monthly1', methods=['GET'])
def api_predict_monthly_past12_get_all():
    # query = db_session.query(MonthlyTable1).order_by(MonthlyTable1.pkey.desc())
    query = "select * from monthly1 ORDER BY pkey desc"
    result = db_session.execute(query)

    return response_json_list(result)


## predic_monthly past12 get
@predic_apis.route('/infer/predict/monthly1/<int:pkey>', methods=['GET'])
def api_predict_monthly_past12_get(pkey):
    # query = db_session.query(MonthlyTable1).filter(MonthlyTable1.pkey == pkey).order_by(MonthlyTable1.pkey.desc())
    query = "select * from monthly1 where pkey=%s"%(pkey)
    result = db_session.execute(query)

    return response_json_value(result)

## predic_daily delete
@predic_apis.route('/infer/predict/monthly1/<int:pkey>', methods=['DELETE'])
def api_predict_monthly1_delete(pkey):
    db = db_session.query(MonthlyTable1).get(pkey)

    area = db.target_area
    start_date = db.start_date
    month_range = db.month_range
    temp_mode = db.temp_option
    sub_mode = db.sub_option

    start_year, start_month, start_day = devide_date(start_date)
    path1 = folder_path + 'result/%d/past_%s_%s_%d_%d_%d_%d_daily' % (
        start_date, area, start_year, start_month, month_range, temp_mode, sub_mode)
    path2 = folder_path + 'result/%d/past_%s_%s_%d_%d_%d_%d_monthly' % (
        start_date, area, start_year, start_month, month_range, temp_mode, sub_mode)

    try:
        print("monthly1_remove_path: ", path1)
        db_session.query(MonthlyTable1).filter(MonthlyTable1.pkey == pkey).delete()
        db_session.commit()

        file_remove(path1)
        file_remove(path2)
    except Exception as e:
        db_session.rollback()
        print(e)
        return jsonify(False)

    return jsonify(True)

## predic_daily get
@predic_apis.route('/infer/predict/monthly1/<int:pkey>/values', methods=['GET'])
def api_predict_monthly1_get_value(pkey):

    # TODO: 디비 정보로 area,yaer,month,day

    db = db_session.query(MonthlyTable1).get(pkey)

    area = db.target_area
    start_date = db.start_date
    month_range = db.month_range
    temp_mode = db.temp_option
    sub_mode = db.sub_option

    start_year, start_month, start_day = devide_date(start_date)

    get_class = get_predic_data()

    # result = dict()
    # # print("monthly1_daily_value: ",value1)
    # # print("monthly1_monthly_value: ",value2)
    #
    # if value_option == 'daily':
    #     result = get_class.get_Monthly_latest_12months_daily_value(area, start_year - 1, start_month, temp_mode,
    #                                                                sub_mode, start_date)
    #
    #
    # elif value_option == 'monthly':
    #     result = get_class.get_Monthly_latest_12months_monthly_value(area, start_year - 1, start_month, temp_mode,
    #                                                                  sub_mode, start_date)
    result = get_class.get_Monthly_latest_12months_monthly_value(area, start_year - 1, start_month, temp_mode,
                                                                     sub_mode, start_date)
    return jsonify(result)
##############################################################################################
########################  Monthly-coming12  ##################################################
##############################################################################################

## predic_monthly coming24 set
## area, start_year, start_month, month_range
## 실행 32분
@predic_apis.route('/infer/predict/monthly2', methods=['POST'])
def api_predict_monthly_coming24_set():
    try:
        req = request.get_json()
        jsonString = json.dumps(req)
        data = json.loads(jsonString)

        sort = data['sort']
        area = data['area']
        model = data['model'] # DB 저장용.
        start_date = data['start_date']

    except:
        abort(400)

    else:
        dt = datetime.datetime.now()

        if not start_date:
            start_date, start_year, start_month, start_day = date_time(dt)
        else:
            start_year, start_month, start_day = devide_date(start_date)

        ## DB에 키가 없을 경우. except로 넘어감.
        try:

            db_session.add(
                MonthlyTable2(target_sort=sort, target_area=area, model_name=model, start_date=start_date,
                              month_range=24))
            db_session.commit()

            detectkey = db_session.query(MonthlyTable2.pkey).order_by(MonthlyTable2.pkey.desc())
            print(detectkey[0][0])

            set_class = set_predic_data()
            set_class.set_Monthly_coming_24months(area, start_year, start_month, 24, start_date, detectkey[0][0])

            final_result = {"id":detectkey[0][0]}

            return jsonify(final_result)
        except:
            return jsonify(False)


## predic_monthly coming get
@predic_apis.route('/infer/predict/monthly2', methods=['GET'])
def api_predict_monthly_coming24_get_all():
    # query = db_session.query(MonthlyTable2).order_by(MonthlyTable2.pkey.desc())
    query = "select * from monthly2 ORDER BY pkey desc"
    result = db_session.execute(query)

    return response_json_list(result)


## predic_monthly past12 get
@predic_apis.route('/infer/predict/monthly2/<int:pkey>', methods=['GET'])
def api_predict_monthly_coming24_get(pkey):
    # query = db_session.query(MonthlyTable2).filter(MonthlyTable2.pkey == pkey).order_by(MonthlyTable2.pkey.desc())
    query = "select * from monthly2 where pkey=%s"%(pkey)
    result = db_session.execute(query)

    return response_json_value(result)

## predic_daily delete
@predic_apis.route('/infer/predict/monthly2/<int:pkey>', methods=['DELETE'])
def api_predict_monthly2_delete(pkey):
    db = db_session.query(MonthlyTable2).get(pkey)

    area = db.target_area
    start_date = db.start_date
    month_range = db.month_range


    start_year, start_month, start_day = devide_date(start_date)
    path1 = folder_path + 'result/%d/coming_%s_%d_%d_%d_daily' % (
        start_date, area, start_year, start_month, month_range)
    path2 = folder_path + 'result/%d/coming_%s_%d_%d_%d_monthly' % (
        start_date, area, start_year, start_month, month_range)

    try:
        db_session.query(MonthlyTable2).filter(MonthlyTable2.pkey == pkey).delete()
        db_session.commit()

        file_remove(path1)
        file_remove(path2)
    except Exception as e:
        db_session.rollback()
        print(e)
        return jsonify(False)

    return jsonify(True)

## predic_daily get
@predic_apis.route('/infer/predict/monthly2/<int:pkey>/values', methods=['GET'])
def api_predict_monthly2_get_value(pkey):

    # TODO: 디비 정보로 area,yaer,month,day

    db = db_session.query(MonthlyTable2).get(pkey)

    area = db.target_area
    start_date = db.start_date
    month_range = db.month_range


    start_year, start_month, start_day = devide_date(start_date)

    get_class = get_predic_data()

    # result = dict()
    # if value_option == 'daily':
    #     result = get_class.get_Monthly_coming_24months_daily_value(area,start_year,start_month,start_date)
    # elif value_option == 'monthly':
    #     result = get_class.get_Monthly_coming_24months_monthly_value(area, start_year, start_month,start_date)
    result = get_class.get_Monthly_coming_24months_monthly_value(area, start_year, start_month, start_date)

    return jsonify(result)

##############################################################################################
########################  Yearly  ############################################################
##############################################################################################

## predic_yearly coming5 set
## area, start_year, start_month, month_range
## 실행 10초 결과 짧음.
@predic_apis.route('/infer/predict/yearly', methods=['POST'])
def api_predict_yearly_coming5_set():
    try:
        req = request.get_json()
        jsonString = json.dumps(req)
        data = json.loads(jsonString)

        sort = data['sort']
        area = data['area']
        model = data['model'] # DB 저장용.
        start_date = data['start_date']

    except:
        abort(400)

    else:
        dt = datetime.datetime.now()

        if not start_date:
            start_date, start_year, start_month, start_day = date_time(dt)
        else:
            start_year, start_month, start_day = devide_date(start_date)

        ## DB에 키가 없을 경우. except로 넘어감.
        try:


            db_session.add(
                YearlyTable(target_sort=sort, target_area=area, model_name=model, start_date=start_date))
            db_session.commit()

            detectkey = db_session.query(YearlyTable.pkey).order_by(YearlyTable.pkey.desc())
            print(detectkey[0][0])

            set_class = set_predic_data()
            set_class.set_Yearly_coming_5years(area, start_year, start_date, detectkey[0][0])

            final_result = {"id": detectkey[0][0]}

            return jsonify(final_result)
        except:
            return jsonify(False)


## predic_yearly coming get
@predic_apis.route('/infer/predict/yearly', methods=['GET'])
def api_predict_yearly_get_all():
    # query = db_session.query(YearlyTable).order_by(YearlyTable.pkey.desc())
    query = "select * from yearly ORDER BY pkey desc"
    result = db_session.execute(query)

    return response_json_list(result)


## predic_yearly get
@predic_apis.route('/infer/predict/yearly/<int:pkey>', methods=['GET'])
def api_predict_yearly_get(pkey):
    # query = db_session.query(YearlyTable).filter(YearlyTable.pkey == pkey).order_by(YearlyTable.pkey.desc())
    query = "select * from monthly2 where pkey=%s"%(pkey)
    result = db_session.execute(query)

    return response_json_value(result)

## predic_yearly delete
@predic_apis.route('/infer/predict/yearly/<int:pkey>', methods=['DELETE'])
def api_predict_yearly_delete(pkey):
    db = db_session.query(YearlyTable).get(pkey)

    area = db.target_area
    start_date = db.start_date
    month_range = db.month_range

    start_year, start_month, start_day = devide_date(start_date)
    path1 = folder_path + 'result/%d/yearly/coming_%s_%d_to_%d_monthly.csv' % (
        start_date, area, start_year, start_year+5)
    path2 = folder_path + 'result/%d/yearly/coming_%s_%d_to_%d_yearly.csv' % (
        start_date, area, start_year, start_year+5)

    try:
        db_session.query(YearlyTable).filter(YearlyTable.pkey == pkey).delete()
        db_session.commit()

        file_remove(path1)
        file_remove(path2)
    except Exception as e:
        db_session.rollback()
        print(e)
        return jsonify(False)

    return jsonify(True)

## predic_daily get
@predic_apis.route('/infer/predict/yearly/<int:pkey>/values', methods=['GET'])
def api_predict_yearly_get_value(pkey):

    # TODO: 디비 정보로 area,yaer,month,day

    db = db_session.query(YearlyTable).get(pkey)

    area = db.target_area
    start_date = db.start_date

    start_year, start_month, start_day = devide_date(start_date)

    get_class = get_predic_data()


    # result = dict()
    # if value_option == 'monthly':
    #     result = get_class.get_Yearly_coming_5years_month(area,start_year, start_date)
    # elif value_option == 'yearly':
    #     result = get_class.get_Yearly_coming_5years_year(area, start_year, start_date)
    result = get_class.get_Yearly_coming_5years_year(area, start_year, start_date)
    return jsonify(result)


##############################################################################################
##############################################################################################
'''
{
        "period": "2019-11-01 10:23:45~2019-11-30 23:59:59",
        "dataset": [
                {
                        "trainedModel": "weather+energy",
                        "arguments": {
                                "resource": "<numeric>ismart!ismart/0330102552/-/usage"
                        }
                }
        ]
}
-------------------------
HYGAS.NAJU_C_HOUSE.30001.1 - 나주_하우스_가스인수량.
HYGAS.NAJU_C_HOUSE.30001.2 - 나주_하우스_가스검침량.
{
        "period": "2019-10-03 10:23:45",
        "dataset": [
                {
                        "trainedModel": "daily",
                        "arguments": {
                                "location":"naju",
                                "resource": "30001.1"
                        }
                }
        ]
}
'''
@predic_apis.route('/infer/predict', methods=['POST'])
@crossdomain(origin='*')
def api_infer_predict_API():
    # try:
    #     key = session['logger']
    #     pkey = db_session.query(Login.pkey).filter(Login.id == str(key))
    #     login = db_session.query(Login).get(pkey)
    # except:
    #     pkey = 0
    # else:
    #     pkey = login.pkey
    user_pkey = get_user_pkey()
    # print(pkey)

    req = request.get_json()
    jsonString = json.dumps(req)
    data = json.loads(jsonString)

    # try:

    period = data['period']
    dataset = data['dataset']

    period_value = get_period_value(period)
    print(period_value)

    period_start_date = '%04d%02d%02d' % (period_value[0], period_value[1], period_value[2])
    period_start_time = '%02d:%02d:%02d' % (period_value[3], period_value[4], period_value[5])
    period_end_date = '%04d%02d%02d' % (period_value[6], period_value[7], period_value[8])
    period_end_time = '%02d:%02d:%02d' % (period_value[9], period_value[10], period_value[11])

    final_result = list()
    # dataset 안에 리스트 형태로
    print("dataset: ",dataset)
    for data_value in dataset:
        filename = str()
        print('--------------2---------------')

        try:
            # trainedmodel은 필수. <스마트:'water+temp'>,<해양:'daily','monthly'..>
            trained_model = data_value['trainedModel']
            print("trained_model: ",trained_model)
            # resource 나 location 값 받을때 상위.
            argument = data_value['arguments']
            print("argument: ",argument)

            ## resource
            # <스마트:'<numeric>ismart!ismart/0330102552/-/usage'>,<해양:'30001.1-인수','30001.2'-검침>
            resource = str(argument['resource'])

            # -------- arguments 안에 있는 변수는 스마트, 해양 같을수도 아닐수도.
            ## location(area) (default = naju)
            try:
                area = argument['location']
                ## 현재 area를 naju로 통일.
                if area != 'naju':
                    area = 'naju'
            except:
                area = 'naju'

            # ## sort (default = insu)
            # try:
            #     sort = argument['sort']
            # except:
            #     sort = 'insu'

            ## temp_mode (default = 0)
            try:
                temp_mode = argument["temp_mode"]
            except:
                temp_mode = 0

            ## sub_mode (default = 0)
            try:
                sub_mode = argument["sub_mode"]
            except:
                sub_mode = 0

            # 현재 스마트경우 받은 모델이 없어서, 임시폴더로 이름 만들어서 임의 값 저장중. (filename)

            file_name_get_model = trained_model.replace('+', '_')
            filename = '%s_%s' % (file_name_get_model, get_arguments_value(resource))


        except Exception as e:
            print(e)
            print('-------11-')
            return abort(400)

        else:

            ## resource가 해양가스 일 때.

            print("Hygas")
            # print(sort)
            # print(area)
            # print(trained_model)
            # print(period_start_date)

            if trained_model == 'daily':
                if int(period_start_date) > 20191005:
                    abort(400)
                result = predict_daily(resource,area,trained_model,int(period_start_date), user_pkey)
                final_result.append(result)
            elif trained_model == 'monthly1':
                if int(period_start_date) > 20191005 or int(period_start_date) < 20150101:
                    abort(400)
                result = predict_monthly1(resource, area, trained_model, int(period_start_date), temp_mode, sub_mode, user_pkey)
                final_result.append(result)
            elif trained_model == 'monthly2':
                if int(period_start_date) > 20191005 or int(period_start_date) < 20170101:
                    abort(400)
                result = predict_monthly2(resource, area, trained_model, int(period_start_date), user_pkey)
                final_result.append(result)
            elif trained_model == 'yearly':
                if int(period_start_date) > 20191005 or int(period_start_date) < 20190101:
                    abort(400)
                result = predict_yearly(resource, area, trained_model, int(period_start_date), user_pkey)
                final_result.append(result)
            ## 스마트 에너지 일 때.
            else:
                if resource.count('.') == 1:
                    abort(400)
                else:
                    model = get_train_model(user_pkey)
                    model.train_model(filename, period_start_date, period_end_date, period_start_time, period_end_time)
                    value = model.train_model_result(filename)

                    ## 최종 적으로 각 모델들의 결과 값들을 합해서 json 형태로 출력 or
                    ## 출력이 long term 이면 결과 파일을 따로 읽는 API 새로 작성.
                    final_result.append(value)

    # return jsonify(True)
    return jsonify(final_result)
    # except Exception as e:
    #     print('----------742----------')
    #     print(e)
    #     abort(400)

@predic_apis.route('/infer/predicted', methods=['GET'])
@crossdomain(origin='*')
def api_infer_predicted_API():
    daily = "select * from daily ORDER BY pkey desc"
    daily = db_session.execute(daily)

    for d1 in daily:
        print(d1)

    monthly1 = "select * from monthly1 ORDER BY pkey desc"
    monthly1 = db_session.execute(monthly1)

    for m1 in monthly1:
        print(m1)

    monthly2 = "select * from monthly2 ORDER BY pkey desc"
    monthly2 = db_session.execute(monthly2)

    for m2 in monthly2:
        print(m2)

    yearly = "select * from yearly ORDER BY pkey desc"
    yearly = db_session.execute(yearly)

    for y1 in yearly:
        print(y1)



    return jsonify(True)


def get_arguments_value(argument):
    # argument = arguments.split('/')
    # argument = argument[0]
    a=0
    value_str = str()
    value = str()

    while(a<len(argument)):
        if argument[a].isalpha() or argument[a].isdigit():
            value_str += argument[a]
        else:
            if value_str:
                value+='%s_'%(value_str)
                value_str = ''
        if a == len(argument)-1:
            value += '%s' % (value_str)
        a += 1
    return value

def get_period_value(period):
    print(period)
    period = period.split('~')
    print('-------------1----------------')

    if len(period) != 2:
        # 기간이 앞에만 있을 경우.
        period = [period[0],period[0]]

    value = list()
    for period_v in period:
        count = 0
        each_value = str()
        valuecheck = list()


        while(count < len(period_v)):
            ## 숫자로 변환.
            try:
                num = int(period_v[count])
            except:
                num = period_v[count]

            ## 숫자이면 값 넣기.
            if isinstance(num, int):
                each_value += period_v[count]
            ## 숫자 아니면 넣은값 저장.
            else:
                if each_value:
                    value.append(int(each_value))
                    valuecheck.append(int(each_value))
                each_value = str()

            count += 1

        ## 나머지 값 저장.
        if count != 0:
            if each_value:
                value.append(int(each_value))
                valuecheck.append(int(each_value))

        ## 날짜 개수가 부족하거나 0값일 경우 400
        if len(valuecheck) < 3:
            return abort(400)

        for i in valuecheck:
            if i == 0:
                abort(400)

        ## 년/월/일/시/분/초 6개가 나와야함.
        if len(valuecheck) != 6:
            ## 부족한 개수만큼 추가.
            aa = 0
            while(aa < 6-len(valuecheck)):
                value.append(int(0))
                aa += 1
    return value

'''
{
  "sort":"insu",
  "area":"naju",
  "model":"boosting light",
  "start_date":20191005
}
'''
def predict_daily(sort,area,model,start_date,user_pkey):
    # print("start_date: ",start_date)

    dt = datetime.datetime.now()

    if not start_date:
        start_date, start_year, start_month, start_day = date_time(dt)
        # 오전 7시에 예보데이터 나옴.
        if dt.hour <= 7:
            start_day = start_day - 1
    else:
        start_year, start_month, start_day = devide_date(start_date)

    daily_output_file = folder_path + 'result/%s/predict_%s_%d_%d_%d_daily' % (user_pkey, area, start_year, start_month, start_day)

    try:
        db_session.add(DailyTable(resource=sort, location=area, model_name=model, start_date=start_date, save_daily=daily_output_file))
        db_session.commit()

        detectkey = db_session.query(DailyTable.pkey).order_by(DailyTable.pkey.desc())
        print(detectkey[0][0])

        set_class = set_predic_data()
        set_class.set_Daily_coming_30days(area, start_year, start_month, start_day, detectkey[0][0])

        final_reuslt = {"dataset": 'daily_'+str(detectkey[0][0])}
        return final_reuslt
    except:
        final_reuslt = {"dataset": None}
        return final_reuslt

'''
        sort = data['sort']
        area = data['area']
        model = data['model']
        start_date = data['start_date']
        temp_mode = data['temp_option']
        sub_mode = data['sub_option']
'''
def predict_monthly1(sort, area, model, start_date, temp_mode, sub_mode, user_pkey):

    if not start_date:
        dt = datetime.datetime.now()
        start_date, start_year, start_month, start_day = date_time(dt)
    else:
        start_year, start_month, start_day = devide_date(start_date)

    try:

        ''' 
        1. 요청날짜가 data/sub,insu(~2019.9보유중),temp(~2019.12보유중)데이터보다 이전 날짜를 만족해야 실행 됨.
        2. 요청한 날짜의 앞뒤로 1년 데이터로 뭐 하는거 같음
        3. 20190701로 하니까 20191001, 20191101 데이터(없는데이터)를 가져오려해서 Error 발생.
        3-2. past12는 과거 1년 날짜로 시작하는게 아닌가 하는 생각이 듬.
        3-3 20181005 날짜로 실행, (2018-10-01 ~ 2019-09-01) 데이터. okay. result/20191005/past~~ 저장.
        '''
        daily_output_file = folder_path + 'result/%d/past_%s_%d_%d_%d_T%d_S%d_daily' % (user_pkey, area, start_year, start_month, 12, temp_mode, sub_mode)
        monthly_output_file = folder_path + 'result/%d/past_%s_%d_%d_%d_T%d_S%d_monthly' % (user_pkey, area, start_year, start_month, 12, temp_mode, sub_mode)

        db_session.add(
            MonthlyTable1(resource=sort, location=area, model_name=model, start_date=start_date,
                          temp_option=temp_mode, sub_option=sub_mode, save_daily=daily_output_file, save_monthly=monthly_output_file))
        db_session.commit()

        detectkey = db_session.query(MonthlyTable1.pkey).order_by(MonthlyTable1.pkey.desc())
        print(detectkey[0][0])

        set_class = set_predic_data()
        set_class.set_Monthly_latest_12months(area, start_year - 1, start_month, 12, temp_mode, sub_mode,
                                              start_date, detectkey[0][0])
        final_result = {"dataset":'monthly1_'+str(detectkey[0][0])}
        return final_result
    except:
        final_result = {"dataset": None}
        return final_result

'''
        sort = data['sort']
        area = data['area']
        model = data['model'] # DB 저장용.
        start_date = data['start_date']
'''
def predict_monthly2(sort,area,model,start_date,user_pkey):

    dt = datetime.datetime.now()

    if not start_date:
        start_date, start_year, start_month, start_day = date_time(dt)
    else:
        start_year, start_month, start_day = devide_date(start_date)

    ## DB에 키가 없을 경우. except로 넘어감.
    try:

        daily_output_file = folder_path + 'result/%d/coming_%s_%d_%d_%d_daily' % (user_pkey, area, start_year, start_month, 24)
        monthly_output_file = folder_path + 'result/%d/coming_%s_%d_%d_%d_monthly' % (user_pkey, area, start_year, start_month, 24)

        db_session.add(
            MonthlyTable2(resource=sort, location=area, model_name=model, start_date=start_date))
        db_session.commit()

        detectkey = db_session.query(MonthlyTable2.pkey).order_by(MonthlyTable2.pkey.desc())
        print(detectkey[0][0])

        set_class = set_predic_data()
        set_class.set_Monthly_coming_24months(area, start_year, start_month, 24, start_date, detectkey[0][0])

        final_result = {"dataset":'monthly2_'+str(detectkey[0][0])}
        return jsonify(final_result)
    except:
        final_result = {"dataset": None}
        return final_result

'''
        sort = data['sort']
        area = data['area']
        model = data['model'] # DB 저장용.
        start_date = data['start_date']

'''
def predict_yearly(sort,area,model,start_date,user_pkey):
    dt = datetime.datetime.now()

    if not start_date:
        start_date, start_year, start_month, start_day = date_time(dt)
    else:
        start_year, start_month, start_day = devide_date(start_date)

    ## DB에 키가 없을 경우. except로 넘어감.
    try:
        result_path = folder_path + 'result/%d/yearly/' % (start_date)
        monthly_save = result_path + 'coming_' + area + '_' + str(start_year) + '_to_' + str(start_year + 5) + '_monthly' + '.csv'
        yearly_save = result_path + 'coming_' + area + '_' + str(start_year) + '_to_' + str(start_year + 5) + '_yearly' + '.csv'

        db_session.add(
            YearlyTable(resource=sort, location=area, model_name=model, start_date=start_date, save_monthly=monthly_save, save_yearly=yearly_save))
        db_session.commit()

        detectkey = db_session.query(YearlyTable.pkey).order_by(YearlyTable.pkey.desc())
        print(detectkey[0][0])

        set_class = set_predic_data()
        set_class.set_Yearly_coming_5years(area, start_year, start_date, detectkey[0][0])

        final_result = {"dataset": 'yearly_'+str(detectkey[0][0])}
        return jsonify(final_result)

    except:
        final_result = {"dataset": None}
        return final_result