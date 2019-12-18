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

'''directory'''
## database
from DB.DataBase.database import db_session, dbsearch
from DB.DataBase.models import Login, ResultTable, LocationTable, ResourceTable, ModelTable

## api helper
from API.api_helper.api_helper import crossdomain, get_query_string, get_query_key, file_remove, devide_date, get_user_key
from API.api_helper.api_helper import post_request, response_json_list, response_json_value, date_time
from API.api_helper.user_directory import folder_prediction_path, root_path
from API.Predict.set_data_class import set_predic_data
from API.Predict.get_data_class import get_predic_data, get_train_model

''' '''
from flask_cors import CORS

predic_apis = Blueprint('predic_d_set_apis', __name__, url_prefix='/api')

wtforms_json.init()


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
=========================

{  
   "period":"2019-11-11 17:00:00~2019-11-30 23:59:59",
   "dataset":[  
      {  
         "trainedModel":"weather+energy",
         "arguments":{  
            "resource":"<numeric>ismart!ismart/0330102552/-/usage"
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
                        "trainedModel": 1,
                        "arguments": {
                                "location":1,
                                "resource": 2
                        }
                }
        ]
}
'''
@predic_apis.route('/infer/predicts', methods=['POST'])
@crossdomain(origin='*')
def api_infer_predict_API():
    user_key = get_user_key()

    req = request.get_json()
    jsonString = json.dumps(req)
    data = json.loads(jsonString)

    try:
        dataset = data['dataset']
    except:
        abort(400)

    try:
        period = data['period']
    except:
        dt = datetime.datetime.now()
        # start_date, start_year, start_month, start_day = date_time(dt)
        period = str(dt.strftime('%Y-%m-%d'))

    # print("period: ",period)

    period_value = get_period_value(period)
    # print(period_value)

    period_start_date = '%04d%02d%02d' % (period_value[0], period_value[1], period_value[2])
    period_start_time = '%02d:%02d:%02d' % (period_value[3], period_value[4], period_value[5])
    period_end_date = '%04d%02d%02d' % (period_value[6], period_value[7], period_value[8])
    period_end_time = '%02d:%02d:%02d' % (period_value[9], period_value[10], period_value[11])

    final_result = list()
    # dataset 안에 리스트 형태로
    # print("dataset: ",dataset)
    for data_value in dataset:
        filename = str()
        # print('--------------2---------------')

        try:
            # trainedmodel은 필수. <스마트:'water+temp'>,<해양:'daily','monthly'..>
            trained_model = data_value['trainedModel']
            argument = data_value['arguments']

            # <스마트:'<numeric>ismart!ismart/0330102552/-/usage'>,<해양:'30001.1-인수','30001.2'-검침>
            resource = argument['resource']

            try:
                ##todo: key 값으로 추출.
                area = argument['location']
                # todo: 현재 폴더에 naju 데이터 뿐이기 때문에, 추후에 다른 지역 데이터 오면 해당 영역 open 여기 수정.
                if not area == 1:
                    area = 1
            except:
                area = 1

            ## monthly1 경우에 temp, sub 모드.
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

            # print("resource: ", resource)
            # print("area: ",area)


            # 현재 스마트경우 받은 모델이 없어서, 임시폴더로 이름 만들어서 임의 값 저장중. (filename)
            if isinstance(trained_model, str):
                if isinstance(resource, int):
                    abort(400)
                else:
                    file_name_get_model = trained_model.replace('+', '_')
                    filename = '%s_%s' % (file_name_get_model, get_arguments_value(resource))

                    model = get_train_model(user_key)
                    model.train_model(filename, period_start_date, period_end_date, period_start_time,
                                      period_end_time)
                    value = model.train_model_result(filename)

                    ## 최종 적으로 각 모델들의 결과 값들을 합해서 json 형태로 출력 or
                    ## 출력이 long term 이면 결과 파일을 따로 읽는 API 새로 작성.
                    final_result.append(value)

            elif isinstance(trained_model, int):
                print('------------1----------------')

                try:
                    quer = db_session.query(ModelTable.id).filter(ModelTable.key == trained_model)
                    records = db_session.execute(quer)
                    for i in records:
                        ## 'naju
                        for x, y in i.items():
                            string_model = y
                except:
                    string_model = 'daily'

                ## resource가 해양가스 일 때.
                # print("Hygas")
                # print(sort)
                # print(area)
                # print(trained_model)
                # print(period_start_date)
                dt = datetime.datetime.now()
                date_check = int(dt.strftime('%Y%m%d'))
                if string_model == 'daily':
                    ## todo: 인수, 검침량 데이터를 읽어서 해당 날짜에 가능한 모델링을 하도록 자동화.
                    '''
                    -오늘에 해당하는 달을 기준으로 한달전 데이터가 모두 있어여함.
                    -insu가 10월6까지 있음 -> 10월30일 요청하면 insu 9.1~9.30까지 불러옴, 
                     11월1일로 요청하면 insu 10.1~10.31일을 써야하는데 없어서 ERROR!
                    -20191130요청시 -> -4년(2015)부터 가져옴 // 20181130년요청시-> -4년(2014)부터 가져옴.
                    -예측 날짜 데이터 (10월 29일 12시 - 11월 6 일 19시) 비어있음.
                    '''
                    # print(period_start_date)
                    # print(date_check)

                    if int(period_start_date) > 20191030:
                        period_start_date = 20191028
                        # abort(400)
                    result = predict_daily(resource, area, trained_model, int(period_start_date), user_key)
                    final_result.append(result)
                elif string_model == 'monthly1':
                    '''
                    인수, 검침량 데이터를 읽어서 해당 날짜에 가능한 모델링을 하도록 자동화.  
                    20191005 날짜로 실행 -> (2018-10-01 ~ 2019-09-30 얻음.) 
                    '''
                    ## todo: db에 유저 key 추가.
                    ## todo: 어떤 날짜 ~ 날짜 데이터로 모델링 하는지 확인 필요.
                    if int(period_start_date) > 20191005 or int(period_start_date) < 20150101:
                        period_start_date = 20191005
                        # abort(400)
                    result = predict_monthly1(resource, area, trained_model, int(period_start_date), temp_mode,
                                              sub_mode, user_key)
                    final_result.append(result)
                elif string_model == 'monthly2':
                    ## todo: 인수, 검침량 데이터를 읽어서 해당 날짜에 가능한 모델링을 하도록 자동화.
                    if int(period_start_date) > 20191005 or int(period_start_date) < 20170101:
                        period_start_date = 20191005
                        # abort(400)
                    result = predict_monthly2(resource, area, trained_model, int(period_start_date), user_key)
                    final_result.append(result)
                elif string_model == 'yearly':
                    ## todo: 인수, 검침량 데이터를 읽어서 해당 날짜에 가능한 모델링을 하도록 자동화.
                    if int(period_start_date) > 20191005 or int(period_start_date) < 20190101:
                        period_start_date = 20191005
                        # abort(400)
                    result = predict_yearly(resource, area, trained_model, int(period_start_date), user_key)
                    # print(result)
                    final_result.append(result)

                else:
                    abort(400)

            # if string_area == 'yearly' or string_area == 'daily' or string_area == 'monthly1' or string_area == 'monthly2':
            message = str(final_result[0])
            filepath = root_path + '/detectkey/'
            if not os.path.isdir(filepath):
                os.mkdir(filepath)
            with open(filepath + message, 'w') as f:
                f.write(message)


        except Exception as e:
            print(e)
            print('----749--')
            return abort(400)

        final_dict = {"dataset":final_result}

    return jsonify(final_dict)
    # except Exception as e:
    #     print('----------742----------')
    #     print(e)
    #     abort(400)


@predic_apis.route('/infer/predicts/valuemake', methods=['GET'])
@crossdomain(origin='*')
def api_infer_predict_make_value():
    files = root_path + '/detectkey/daily_12'
    with open(files,'w') as f:
        f.write("daily_12")

@predic_apis.route('/infer/predicts', methods=['GET'])
@crossdomain(origin='*')
def api_infer_predicted_API():

    limit = request.args.get('limit', type=int)
    page = request.args.get('page', type=int)
    # print(limit)
    # print(page)

    result = []
    dict_result = {}

    query = "select key, resource, location, model ,start_date as period, inserted, finished from result_save ORDER BY key desc"
    query_value = db_session.execute(query)

    for y1 in query_value:
        modelkey = y1[3]
        try:
            quer = db_session.query(ModelTable.id).filter(ModelTable.key == modelkey)
            records = db_session.execute(quer)
            for i in records:
                ## 'naju
                for x, y in i.items():
                    string_model = y
        except:
            string_model = 'daily'

        # print(y1.items())
        value_dict = {}
        get_insert_time = None
        get_finish_time = None
        for x, y in y1.items():
            ## start_date에 각 모델에 맞춰 기간 계산.
            if 'period' in x:
                if string_model == 'daily':
                    value_dict.update({x: datecount(y, 'daily') + ' ~ ' + datecount(y + 29, 'daily')})
                elif string_model == 'monthly1':
                    value_dict.update({x: datecount(y - 10000, 'monthly1') + ' ~ ' + datecount(y, 'monthly1')})
                elif string_model == 'monthly2':
                    value_dict.update({x: datecount(y, 'monthly2') + ' ~ ' + datecount(y + 20000, 'monthly2')})
                elif string_model == 'yearly':
                    value_dict.update({x: datecount(y, 'yearly') + ' ~ ' + datecount(y + 50000, 'yearly')})
            elif 'inserted' == str(x):
                get_insert_time = y
                # print(y)
            elif 'finished' == str(x):
                get_finish_time = y
                # print(y)
            else:
                value_dict.update({x: y})



        try:
            from datetime import timedelta, datetime
            ## 종료-시작 ( 종료가 안됐다면 None값)
            exe_time = (get_finish_time-get_insert_time).seconds
            # print("time: ",exe_time)
            value_dict.update({"exe_time": exe_time})
        except:
            value_dict.update({"exe_time": None})


        result.append(value_dict)


    if limit == None or limit == 0:
        if page == None or page == 1:
            result = result
        else:
            result = result[0:0]

    else:
        if page == None or page == 0:
            page = 1

        result_start = limit * page - limit
        result_end = limit * page

        # print("restart: ", result_start)
        # print("reend: ", result_end)

        result = result[result_start:result_end]


    '''
    limit=5
    p1 - 0-5
    p2 - 5-10
    p3 - 10-15
    daily5,4,3,2,1/monthly1_1/monthly2_4,3,2,1/yearly5,4,3,2,1
    '''

    return response_json_list(result)

@predic_apis.route('/infer/predicts/<int:key>', methods=['GET'])
@crossdomain(origin='*')
def api_infer_predicted_API_detail(key):
    limit = request.args.get('limit', type=int)
    page = request.args.get('page', type=int)
    # print(limit)
    # print(page)

    result = []
    dict_result = {}

    query = "select key, resource, location, model ,start_date as period, inserted, finished from result_save where key=%d"%(key)
    query_value = db_session.execute(query)

    for y1 in query_value:
        modelkey = y1[3]
        try:
            quer = db_session.query(ModelTable.id).filter(ModelTable.key == modelkey)
            records = db_session.execute(quer)
            for i in records:
                ## 'naju
                for x, y in i.items():
                    string_model = y
        except:
            string_model = 'daily'

        # print(y1.items())
        value_dict = {}
        get_insert_time = None
        get_finish_time = None
        for x, y in y1.items():
            ## start_date에 각 모델에 맞춰 기간 계산.
            if 'period' in x:
                if string_model == 'daily':
                    value_dict.update({x: datecount(y, 'daily') + ' ~ ' + datecount(y + 29, 'daily')})
                elif string_model == 'monthly1':
                    value_dict.update({x: datecount(y - 10000, 'monthly1') + ' ~ ' + datecount(y, 'monthly1')})
                elif string_model == 'monthly2':
                    value_dict.update({x: datecount(y, 'monthly2') + ' ~ ' + datecount(y + 20000, 'monthly2')})
                elif string_model == 'yearly':
                    value_dict.update({x: datecount(y, 'yearly') + ' ~ ' + datecount(y + 50000, 'yearly')})
            elif 'inserted' == str(x):
                get_insert_time = y
                # print(y)
            elif 'finished' == str(x):
                get_finish_time = y
                # print(y)
            else:
                value_dict.update({x: y})

        try:
            from datetime import timedelta, datetime
            ## 종료-시작 ( 종료가 안됐다면 None값)
            exe_time = (get_finish_time - get_insert_time).seconds
            # print("time: ",exe_time)
            value_dict.update({"runningTime": exe_time})
        except:
            value_dict.update({"runningTime": None})

        result.append(value_dict)

    if limit == None or limit == 0:
        if page == None or page == 1:
            result = result
        else:
            result = result[0:0]

    else:
        if page == None or page == 0:
            page = 1

        result_start = limit * page - limit
        result_end = limit * page

        # print("restart: ", result_start)
        # print("reend: ", result_end)

        result = result[result_start:result_end]

    '''
    limit=5
    p1 - 0-5
    p2 - 5-10
    p3 - 10-15
    daily5,4,3,2,1/monthly1_1/monthly2_4,3,2,1/yearly5,4,3,2,1
    '''

    return response_json_list(result)

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
    # print(period)
    period = period.split('~')
    # print('-------------1----------------')

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

        # print(valuecheck[0:3])
        for i in valuecheck[0:3]:
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


def predict_daily(resource, area, model, start_date, user_key):
    # print("start_date: ",start_date)
    ## sort = 30001.1
    ## area = 'naju'
    dt = datetime.datetime.now()

    if not start_date:
        start_date, start_year, start_month, start_day = date_time(dt)
        # print('-------22------------')
        # 오전 7시에 예보데이터 나옴.
        if dt.hour <= 7:
            start_day = start_day - 1
    else:
        start_year, start_month, start_day = devide_date(start_date)
        # print('-------11------------')

    # ## insu, 30001.1
    # string_resource, mach_resource= resource_define(resource)
    ## naju
    predictarea = area_define(area)
    print("predictarea: ",predictarea)

    daily_output_file = folder_prediction_path + 'result/%s/predict_%s_%d_%d_%d_daily' % (user_key, predictarea, start_year, start_month, start_day)
    print("outputfile: ", daily_output_file)

    try:
        print('-----------2---------------')
        # print("200000: ",start_year, start_month, start_day)
        # db_session.add(DailyTable(resource=sort, location=area, model=model, start_date=start_date, save_daily=daily_output_file))
        db_session.add(ResultTable(resource=resource, location=area, model=model, start_date=start_date, save_file1=daily_output_file, user_key=user_key))
        db_session.commit()
        print('-----------3---------------')

        detectkey = db_session.query(ResultTable.key).order_by(ResultTable.key.desc())
        # print(detectkey[0][0])
        print('-----------4---------------')

        set_class = set_predic_data()
        set_class.set_Daily_coming_30days(predictarea, start_year, start_month, start_day, user_key, detectkey[0][0])
        final_reuslt = detectkey[0][0]
        print('-----------5---------------')
        return final_reuslt
    except:
        final_reuslt = None
        return final_reuslt


def predict_monthly1(resource, area, model, start_date, temp_mode, sub_mode, user_key):

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
        3-3 20181005 날짜로 실행, (2018-10-01 ~ 2019-09-30) 데이터. okay. result/20191005/past~~ 저장.
        3-4 결론적으로 start_year에 -1로 시작했음.
        '''

        predictarea = area_define(area)

        daily_output_file = folder_prediction_path + 'result/%d/past_%s_%d_%d_%d_T%d_S%d_daily' % (user_key, predictarea, start_year, start_month, 12, temp_mode, sub_mode)
        monthly_output_file = folder_prediction_path + 'result/%d/past_%s_%d_%d_%d_T%d_S%d_monthly' % (user_key, predictarea, start_year, start_month, 12, temp_mode, sub_mode)

        # db_session.add(MonthlyTable1(resource=sort, location=area, model=model, start_date=start_date, temp_option=temp_mode, sub_option=sub_mode, save_daily=daily_output_file, save_monthly=monthly_output_file))
        db_session.add(ResultTable(resource=resource, location=area, model=model, start_date=start_date, temp_option=temp_mode, sub_option=sub_mode, save_file2=daily_output_file, save_file1=monthly_output_file, user_key=user_key))
        db_session.commit()

        detectkey = db_session.query(ResultTable.key).order_by(ResultTable.key.desc())
        print(detectkey[0][0])

        set_class = set_predic_data()
        set_class.set_Monthly_latest_12months(predictarea, start_year - 1, start_month, 12, temp_mode, sub_mode,
                                              start_date, user_key, detectkey[0][0])
        final_result = detectkey[0][0]
        return final_result
    except:
        final_result = None
        return final_result


def predict_monthly2(resource, area, model, start_date, user_key):

    dt = datetime.datetime.now()

    if not start_date:
        start_date, start_year, start_month, start_day = date_time(dt)
    else:
        start_year, start_month, start_day = devide_date(start_date)

    ## DB에 키가 없을 경우. except로 넘어감.
    try:

        predictarea = area_define(area)

        daily_output_file = folder_prediction_path + 'result/%d/coming_%s_%d_%d_%d_daily' % (user_key, predictarea, start_year, start_month, 24)
        monthly_output_file = folder_prediction_path + 'result/%d/coming_%s_%d_%d_%d_monthly' % (user_key, predictarea, start_year, start_month, 24)

        db_session.add(ResultTable(resource=resource, location=area, model=model, start_date=start_date, save_file1=monthly_output_file, save_file2=daily_output_file, user_key=user_key))
        db_session.commit()

        detectkey = db_session.query(ResultTable.key).order_by(ResultTable.key.desc())
        print(detectkey[0][0])

        set_class = set_predic_data()
        set_class.set_Monthly_coming_24months(predictarea, start_year, start_month, 24, start_date, user_key, detectkey[0][0])

        final_result = detectkey[0][0]
        return final_result
    except:
        final_result = None
        return final_result


def predict_yearly(resource, area, model, start_date, user_key):
    dt = datetime.datetime.now()

    if not start_date:
        start_date, start_year, start_month, start_day = date_time(dt)
    else:
        start_year, start_month, start_day = devide_date(start_date)

    ## DB에 키가 없을 경우. except로 넘어감.
    try:
        predictarea = area_define(area)

        result_path = folder_prediction_path + 'result/%d/yearly/' % (user_key)
        monthly_save = result_path + 'coming_' + predictarea + '_' + str(start_year) + '_to_' + str(
            start_year + 5) + '_monthly' + '.csv'
        yearly_save = result_path + 'coming_' + predictarea + '_' + str(start_year) + '_to_' + str(
            start_year + 5) + '_yearly' + '.csv'

        # todo: 2.진행률 %로 가능한지. 3.스마트에너지(lwm2m) 체크
        # todo: 5.마크베이스. 7.celery(cpu,gpu)제한, 2개이상이 구동 힘듬. 8. 유저폴더안에, 날짜폴더 추가 할 건지.

        # db_session.add(YearlyTable(resource=sort, location=area, model=model, start_date=start_date, save_monthly=monthly_save, save_yearly=yearly_save))
        db_session.add(
            ResultTable(resource=resource, location=area, model=model, start_date=start_date, save_file1=yearly_save,
                        save_file2=monthly_save, user_key=user_key))
        db_session.commit()

        detectkey = db_session.query(ResultTable.key).order_by(ResultTable.key.desc())
        # print(detectkey[0][0])

        set_class = set_predic_data()
        set_class.set_Yearly_coming_5years(predictarea, start_year, start_date, user_key, detectkey[0][0])

        final_result = detectkey[0][0]
        return final_result




    except:

        final_result = None
        return final_result

def datecount(value, sort):
    syear, smonth, sday = devide_date(value)
    result = str()

    if sday > 28:
        if smonth == 2:
            if sday - 28 > 0:
                sday = sday - 28
                smonth += 1

        elif smonth == 4 or 6 or 9 or 11:
            if sday - 30 > 0:
                sday = sday - 30
                smonth += 1

        elif smonth == 1 or 3 or 5 or 7 or 8 or 10 or 12:
            if sday - 31 > 0:
                sday = sday - 31
                smonth += 1

    if smonth > 12:
        scount = int(smonth / 12)
        smonth = smonth - (12 * scount)
        syear += scount

    if sort == 'daily':
        result = '%02d-%02d-%02d' % (syear, smonth, sday)
    elif sort == 'monthly1' or sort == 'monthly2':
        result = '%02d-%02d-01' % (syear, smonth)
    elif sort == 'yearly':
        result = '%02d-01-01' % (syear)

    return result



def resource_define(resource):
    try:
        # todo: 현재 resource(2,3)은 인수량,검침량으로 이 두개는 name=insu값을 가짐(검침량도 인수량으로 대체하라는 오더).
        ## 그런데 나머지 resource(1,4)는 temp, sub 값을 가지는데, insu데이터와 파일 구조가 달라서 얻는 값들을 따로 정의 해줘야함.
        ## 현재는 1,4도 name을 insu로 지정해 주겠음.
        if resource == 1 or resource == 4:
            resource = 2

        quer = db_session.query(ResourceTable.name, ResourceTable.id).filter(ResourceTable.key == resource)
        records = db_session.execute(quer)
        for i in records:
            for x, y in i.items():
                ## insu
                if x == 'resource_name':
                    string_resource = y
                ##30001.1
                if x == 'resource_id':
                    mach_resource = y
        return string_resource, mach_resource

    except:
        ## resource(1,2,3,4)를 제외한 값도 일단은 가장 기본 값인 resource(1)의  insu, 30001.1 지정.
        string_resource = 'insu'
        mach_resource = '30001.1'
        return string_resource, mach_resource

def area_define(area):
    try:
        quer = db_session.query(LocationTable.id).filter(LocationTable.key == area)
        records = db_session.execute(quer)
        for i in records:
            ## 'naju
            for x, y in i.items():
                string_area = y

        return string_area
    except:
        string_area = 'naju'
        return string_area