# -*- coding: utf-8 -*-
# predic_dedail set API

'''general'''
import json
import datetime
import os
import sys
import time
import random
import string
'''library'''
## flask(REST-API)
from flask import Blueprint, jsonify, send_from_directory, abort, session, send_file
from flask import make_response, request, current_app, Response
from werkzeug.utils import secure_filename
import pandas as pd
from werkzeug.datastructures import FileStorage
# import werkzeug
'''directory'''
from DB.DataBase.database import db_session, dbsearch, dbsearch1
from DB.DataBase.models import DailyTable, MonthlyTable1, MonthlyTable2, YearlyTable, Login
from API.api_helper.user_directory import folder_path3, folder_path
from API.api_helper.api_helper import response_json_value, response_json_list
import collections
from sqlalchemy import func

''' '''
from flask_cors import CORS
import tempfile

data_apis = Blueprint('data_upload_apis', __name__, url_prefix='/api')



@data_apis.route('/attach', methods=['GET', 'POST'])
def file_attach():
    print("file_attach")
    if request.method == 'POST':

        now = datetime.datetime.now()
        nowDate = now.strftime('%Y%m%d')
        nowTime = now.strftime('%H%M%S')
        strtime = 'temp_'+ nowDate + nowTime+'_'
        file_list = list()

        if not os.path.isdir(folder_path3):
            os.mkdir(folder_path3)

        for f in request.files.getlist('file-key'):
            f.save(folder_path3 + secure_filename(strtime+f.filename))
            file_list.append(strtime+f.filename)

        result = {"file-key":file_list}

        return jsonify(result)
        # return jsonify(file_list)

# @data_apis.route('/file', methods=['POST', 'GET'])
# def file_creaaawte():
#
#
#     if request.headers['Content-Type'] == 'text/plain':
#         print(request.headers)
#
#     return jsonify(True)


@data_apis.route('/files', methods=['POST', 'GET'])
def file_create():

    try:
        print("file_create")
        req = request.get_json()
        jsonString = json.dumps(req)
        data = json.loads(jsonString)

        print(data['file-key'])
        # 한개만 받아올때 리스트 씌워서 작업.
        data = [data['file-key']]

        datacount = 0
        for i in data:

            data[datacount] = folder_path3 + i
            datacount += 1

        ## temp 붙은거 삭제.
        for name in data:
            # 실행 중인 파일 수정 금지.
            if sys.argv[0].split("\\")[-1] == name:
                continue

            new_name = name.replace('temp_', '')
            try:
                os.rename(name, new_name)
            except:
                pass

        files = os.listdir(folder_path3)

        ## temp 붙은 파일 삭제 (추후 자동 업데이트로)
        for i in files:
            if 'temp' in i:
                try:
                    os.remove(folder_path3 + i)
                except:
                    pass

        return jsonify(True)

    except Exception as e:
        return jsonify(True)

## ReadAll files
@data_apis.route('/filelist', methods=['GET'])
def api_file_search():
    files = os.listdir(folder_path3)

    return jsonify(files)


@data_apis.route('/datasets/locations', methods=['GET'])
def datasets_locations():
    location_list = ["gwangju", "naju", "jangsung", "damyang"]
    return jsonify(location_list)
'''
HYGAS.NAJU_C_HOUSE.30001.1 - 나주_하우스_가스인수량.
HYGAS.NAJU_C_HOUSE.30001.2 - 나주_하우스_가스검침량.
"resource": "HYGAS.NAJU_C_HOUSE.30001.1"
{
        "period": "2019-11-01 10:23:45~2019-11-30 23:59:59",
        "dataset": [
                {
                        "arguments": {
                                "location":"naju",
                                "resource": "HYGAS.NAJU.30001.1"
                        }
                }
        ]
}
--------------------------------------
{
        "period": "2014-11-01 10:23:45~2019-11-30 23:59:59",
        "dataset": [
                {
                        "source":" hygas",
                        "location": "naju",
                        "useKind": "house",
                        "resource": "30001.1"
                }
        ]
}
'''
## Readall
@data_apis.route('/datasets', methods=['POST'])
def api_data_search_all():
    try:
        key = session['logger']
        pkey = db_session.query(Login.pkey).filter(Login.id == str(key))
        login = db_session.query(Login).get(pkey)
    except:
        pkey = 0
    else:
        pkey = login.pkey

    req = request.get_json()
    jsonString = json.dumps(req)
    data = json.loads(jsonString)

    try:
        period = data['period']
        ## 날짜시간 [2018, 3, 10, 1, 0, 0, 2019, 3, 6, 1, 0, 0] -> 리스트 len = 12
        period_value = get_period_value(str(period))
        # print(period_value)
        # datestart = '%04d-%02d-%02d' % (period_value[0], period_value[1], period_value[2])
        # dateend = int('%04d' % (period_value[6]))
        dateend = 2019
        # print(dateend)
        # datestart = int('%04d' % (period_value[0]))
        datestart = 2014
        # print(datestart)
        datelist = []
        # for i in range(dateend - datestart + 1):
        for i in range(6):
            datelist.append(datestart)
            datestart += 1

    except:
        period = None

    try:
        dataset = data['dataset']
    except Exception as e:
        print('212: ',e)
        abort(400)

    final_result_dict = dict()
    final_result_list = list()
    meta_get = {}
    # print(dataset)
    for data in dataset:
        meta_get2 = []

        print("data: ",data)

        try:
            # argument = data['arguments']
            resource = data['resource']
            area = data['location']
            ## 지역이 나주가 아니면 naju로 강제 변환.
            if not area == 'naju':
                area = 'naju'

        except Exception as e:
            print(e)
            return abort(400)

        try:
            source = data['source']
        except:
            source = 'HYGAS'

        try:
            kind = data['useKind']
        except:
            kind = 'house'

            # todo: csv 파일로 가져왔을때, 문제가 있는거 같다. 같은 값인데, 에러가 난다.
        else:
            dataname = str()
            # print(resource.count('.'))
            if resource.count('.') == 1:
                final_value_list=[]
                # print("datelist: ",datelist)
                for ddstart in datelist:

                    # print("ddstart: ",ddstart)

                    path = folder_path + 'data/insu/%s_insu_%d' % (area.lower(), ddstart)
                    # print(path)
                    dataname = 'insu_sum'
                    ## '/home/uk/PredictionServer/prediction/prediction_ETRI/data/insu/naju_insu_2019'
                    # with open(path, 'r') as f:
                    #     dataname_get = f.readline().strip()

                    with open(path, 'r') as f:
                        dataname_get = f.readlines()

                    data_t = []
                    count = 0
                    data_name = []
                    data_t_month_check=1
                    data_t_value = 0
                    for ii in dataname_get:
                        # data_t.append(ii[:-1].replace('\t',' '))
                        if count == 0:
                            ## 년월일 뺴고 나머지.
                            # data_name = ii[:-1].replace('\t',' ').split(' ')[3:]
                            ##리스트 마지막.
                            data_name = ii[:-1].replace('\t', ' ').split(' ')[-1]
                        else:
                            data_t_month = int(ii[:-1].replace('\t', ' ').split(' ')[1])
                            # print(data_t_month)
                            if data_t_month == data_t_month_check:
                                data_t_value += int(ii[:-1].replace('\t', ' ').split(' ')[-1])
                            else:
                                # data_t.append({data_t_month_check:data_t_value})
                                ## 각 달의 값을 append
                                data_t.append(data_t_value)
                                data_t_value = 0
                                data_t_month_check += 1

                        if count ==1 and ddstart == 2014:
                            ## 처음꺼 몇월 몇일 인지.
                            data_start_date = ii[:-1].replace('\t', ' ').split(' ')[0:3]


                        if count == len(dataname_get)-1:
                            ## 받아온 값의 마지막 꺼 체크해서 나머지 append
                            # data_t.append({data_t_month_check: data_t_value})
                            data_t.append(data_t_value)
                            ## 마지막꺼 몇월 몇일 인지.
                            data_end_date = ii[:-1].replace('\t', ' ').split(' ')[0:3]

                        count += 1
                    # data_name = data_t[0].split(' ')[3:]
                    # print(data_t)

                    # tqq = []
                    #
                    #
                    #
                    # meta_get.update(
                    #     {str(area).upper() + '.' + str(resource): {"beginData": tqq[0], "endDate": tqq[-1]}})
                    # meta = {}
                    # meta["meta"] = meta_get
                    # final_result2.update(meta)

                    data_t.insert(0,ddstart)
                    final_value_list.append(data_t)
                    # final_value_list.append({ddstart:data_t})

            meta_get2.append({"beginDate": '%04d-%02d-%02d'%(int(data_start_date[0]),int(data_start_date[1]),int(data_start_date[2])), "endDate": '%04d-%02d-%02d'%(int(data_end_date[0]),int(data_end_date[1]),int(data_end_date[2]))})

            final_value_list.insert(0,['date',1,2,3,4,5,6,7,8,9,10,11,12])
            meta_get.update({str(source).upper()+'.'+str(resource):meta_get2})

            meta={}
                    # print(final_result2)
            meta["meta"] = meta_get


        final_result_list.append({str(source).upper()+'.'+str(resource):final_value_list})
    final_result_list.append({"meta":meta_get})
                # final_value_list.append(meta)



    return jsonify(final_result_list)




## Read
@data_apis.route('/datasets/<int:pkey>', methods=['GET'])
def api_data_search(pkey):
    pass


## Delete
@data_apis.route('/datasets/<int:pkey>', methods=['DELETE'])
def api_data_delete(pkey):
    pass

@data_apis.route('/datasets/dbtest', methods=['GET'])
def api_data_get_smart_city():
    # query = "select * from login"
    # records = dbsearch.execute(query)


    # query = "select * from UPPER('GWANJUCHALLENGE')_acc_inflow"
    query = "select * from dataset_acc_outflow"
    # query = "select * from initcap('GWANJUCHALLENGE_acc_inflow')"
    # query = "SELECT * FROM dataset_acc_inflow GROUP BY date ORDER BY 1"

    # query = db_session.query(Login)
    # print(query.all())
    records = dbsearch1.execute(query)

    print("records: ",records)

    recn = []
    for row_n in records:
        recn.append(dict(row_n))

    return response_json_list(recn)
########################################################################################
## 통합 values
'''
{
  "period":"2018/03/10 1 ~ 2019/03/06 1 ",
  "dataset": [
		"HYGAS.NAJU_C_all.30001.1" (나주,all,가스인수량),
		"HYGAS.NAJU_C_all.30001.2" (나주,all,가스검침량),
		1 
	]
}
--------------------------------------------------------------
Post(문화전당)
{
  "period":"2017-11-06 1 ~ 2017-12-30 1 ",
  "dataset": [
		"static/acc-inflow",
        "static/acc-outflow",
         {
            "source":" hygas",
            "location": "naju",
            "useKind": "house",
            "resource": "30001.1"
        }
	]
}

---------------------------------------------

{
  "period":"2017-11-06 1 ~ 2017-12-30 1 ",
  "dataset": [
		"static/acc-inflow",
        "static/acc-outflow",
         {
            "source":" hygas",
            "location": "naju",
            "useKind": "house",
            "resource": "30001.1"
        }, {
            "source":" hygas",
            "location": "naju",
            "useKind": "house",
            "resource": "30001.2"
        }
	]
}
'''


@data_apis.route('/datasets/values', methods=['POST'])
def api_data_values():

    try:
        key = session['logger']
        pkey = db_session.query(Login.pkey).filter(Login.id == str(key))
        login = db_session.query(Login).get(pkey)
    except:
        pkey = 0
    else:
        pkey = login.pkey

    req = request.get_json()
    jsonString = json.dumps(req)
    data = json.loads(jsonString)

    try:
        period = data['period']
        ## 날짜시간 [2018, 3, 10, 1, 0, 0, 2019, 3, 6, 1, 0, 0] -> 리스트 len = 12
        period_value = get_period_value(str(period))
        print(period_value)
        datestart = '%04d-%02d-%02d' % (period_value[0], period_value[1], period_value[2])
        dateend = '%04d-%02d-%02d' % (period_value[6], period_value[7], period_value[8])

        ## 해양도시 insu값 무조건 다 출력.
        datestart_hy = 2014
        dateend_hy = 2019
        # print(datestart)
        datelist = []
        # for i in range(dateend - datestart + 1):
        ## range=6 (2014_2019)
        for i in range(6):
            datelist.append(datestart_hy)
            datestart_hy += 1

    except:
        period = None
        datestart_hy = 2014
        dateend_hy = 2019
        datelist = []
        # for i in range(dateend - datestart + 1):
        for i in range(6):
            datelist.append(datestart_hy)
            datestart_hy += 1

    try:
        dataset = data['dataset']
    except Exception as e:
        print('212: ',e)
        abort(400)

    #------------------------------------------------------------
    total_value = dict()
    total_value2 = list()
    meta_get = {}
    meta_get_list = list()
    for i in dataset:
        meta_get2 = []
        print(i)
        if isinstance(i, str):
            if 'static' in i:
                datasetvalue = dataset_check(str(i))
                print(period)

                try:
                    if period:
                        ## datestart: 2019-10-30, dateend: 2019-12-31
                        datasetdate = " where DATE(date) BETWEEN '%s' AND '%s'" % (datestart, dateend)
                        query = "select * from %s%s" % (datasetvalue, datasetdate)
                    else:
                        query = "select * from %s" % (datasetvalue)


                    # if datasetvalue == 'dataset_acc_inflow':
                    #     query = "select	date, dow as week, sum(in_flow) as flow from dataset_acc_inflow " + datasetdate + " group by date, dow order by date"
                    #
                    # # query = "select	date, dow as week, sum(in_flow) as flow from "+datasetvalue+" group by date, dow order by date limit 100"
                    # elif datasetvalue == 'dataset_acc_outflow':
                    #     query = "select	date, dow as week, sum(out_flow) as flow from dataset_acc_outflow " + datasetdate + " group by date, dow order by date"
                    records = dbsearch1.execute(query)
                    result = []

                    import operator
                    count = 0
                    for row_n in records:
                        valueaa = []
                        key_count = 0
                        keyaa = []


                        for x, y in row_n.items():
                            valueaa.extend([y])

                            if key_count == 0:
                                keyaa.extend([x])

                            if count == 0:
                                datestart = valueaa[0]


                        # if count == len(records):
                        #     dateend = valueaa[0]
                        count += 1
                        key_count += 1



                        # row_n = [row_n]

                        # print(row_n)
                        # print(type(row_n))
                        # print(row_n[0])
                        # row_n[0] = str(item.get('date'))

                        # cc=str(cc).split(',')[0]
                        # print(type(cc))
                        result.append(valueaa)
                        # result.append(row_n)

                    dateend = result[-1][0]
                    print(dateend)

                    result.insert(0, keyaa)
                    # print(result)
                    print("result: ",result)
                    ss = {}
                    ss[i] = result
                    total_value.update(ss)
                    total_value2.append(result)

                    meta_get2.append({"beginDate": datestart, "endDate":dateend})
                    meta_get.update({str(i): meta_get2})
                    meta_get_list.extend(meta_get2)
                    print("meta_get: ",meta_get)

                except Exception as e:
                    print(e)
                    # ss = {}
                    # ss[str(i)] = None
                    # total_value.update(ss)
                    total_value2.append([])
                    meta_get_list.append([])
                    pass

            else:
                # ss={}
                # ss[str(i)] = None
                # total_value.update(ss)
                total_value2.append([])
                meta_get_list.append([])
                pass

        elif isinstance(i,dict):
            try:
                # argument = data['arguments']
                resource = i['resource']
                area = i['location']
                ## 지역이 나주가 아니면 naju로 강제 변환.
                if not area == 'naju':
                    area = 'naju'

            except Exception as e:
                print(e)
                return abort(400)

            try:
                source = i['source']
            except:
                source = 'HYGAS'

            try:
                kind = i['useKind']
            except:
                kind = 'house'

                # todo: csv 파일로 가져왔을때, 문제가 있는거 같다. 같은 값인데, 에러가 난다.
            else:
                dataname = str()
                # print(resource.count('.'))
                if resource.count('.') == 1:
                    final_value_list = []
                    # print("datelist: ",datelist)
                    for ddstart in datelist:

                        # print("ddstart: ",ddstart)

                        path = folder_path + 'data/insu/%s_insu_%d' % (area.lower(), ddstart)
                        # print(path)
                        dataname = 'insu_sum'
                        ## '/home/uk/PredictionServer/prediction/prediction_ETRI/data/insu/naju_insu_2019'
                        # with open(path, 'r') as f:
                        #     dataname_get = f.readline().strip()

                        with open(path, 'r') as f:
                            dataname_get = f.readlines()

                        data_t = []
                        count = 0
                        data_name = []
                        data_t_month_check = 1
                        data_t_value = 0
                        for ii in dataname_get:
                            # data_t.append(ii[:-1].replace('\t',' '))
                            if count == 0:
                                ## 년월일 뺴고 나머지.
                                # data_name = ii[:-1].replace('\t',' ').split(' ')[3:]
                                ##리스트 마지막.
                                data_name = ii[:-1].replace('\t', ' ').split(' ')[-1]
                            else:
                                data_t_month = int(ii[:-1].replace('\t', ' ').split(' ')[1])
                                # print(data_t_month)
                                if data_t_month == data_t_month_check:
                                    data_t_value += int(ii[:-1].replace('\t', ' ').split(' ')[-1])
                                else:
                                    # data_t.append({data_t_month_check:data_t_value})
                                    ## 각 달의 값을 append
                                    data_t.append(data_t_value)
                                    data_t_value = 0
                                    data_t_month_check += 1

                            if count == 1 and ddstart == 2014:
                                ## 처음꺼 몇월 몇일 인지.
                                data_start_date = ii[:-1].replace('\t', ' ').split(' ')[0:3]

                            if count == len(dataname_get) - 1:
                                ## 받아온 값의 마지막 꺼 체크해서 나머지 append
                                # data_t.append({data_t_month_check: data_t_value})
                                data_t.append(data_t_value)
                                ## 마지막꺼 몇월 몇일 인지.
                                data_end_date = ii[:-1].replace('\t', ' ').split(' ')[0:3]

                            count += 1

                        data_t.insert(0, ddstart)
                        final_value_list.append(data_t)


                meta_get2.append({"beginDate": '%04d-%02d-%02d' % (
                int(data_start_date[0]), int(data_start_date[1]), int(data_start_date[2])),
                                  "endDate": '%04d-%02d-%02d' % (
                                  int(data_end_date[0]), int(data_end_date[1]), int(data_end_date[2]))})

                final_value_list.insert(0, ['date', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
                meta_get.update({str(source).upper() + '.' + str(resource): meta_get2})
                meta_get_list.extend(meta_get2)

            total_value.update({str(source).upper()+'.'+str(resource):final_value_list})
            total_value2.append(final_value_list)

        else:
            ss = {}
            ss[str(i)] = None
            total_value.update(ss)
            total_value2.append([])
            meta_get_list.append([])


        meta = {}
            # print(final_result2)
        meta["meta"] = meta_get

        # total_value.update(meta)


    # dataset_value = get_HYGAS_dataset_value(pkey, dataset, period_value)
    print(total_value)
    print(type(total_value))
    kk={'dataset':total_value}
    kk.update(meta)

    sdsd={"dataset":total_value2,"meta":meta_get_list}

    # kk = {}
    # kk['datasets'] = total_value
    # total_value.update(kk)
    # print(total_value)
    return jsonify(sdsd)

@data_apis.route('/analysis', methods=['POST'])
def api_analysis():

    try:
        key = session['logger']
        pkey = db_session.query(Login.pkey).filter(Login.id == str(key))
        login = db_session.query(Login).get(pkey)
    except:
        pkey = 0
    else:
        pkey = login.pkey

    req = request.get_json()
    jsonString = json.dumps(req)
    data = json.loads(jsonString)

    try:
        period = data['period']
        ## 날짜시간 [2018, 3, 10, 1, 0, 0, 2019, 3, 6, 1, 0, 0] -> 리스트 len = 12
        period_value = get_period_value(str(period))
        print(period_value)
        datestart = '%04d-%02d-%02d' % (period_value[0], period_value[1], period_value[2])
        dateend = '%04d-%02d-%02d' % (period_value[6], period_value[7], period_value[8])
    except:
        period = None

    try:
        dataset = data['dataset']

    except Exception as e:
        print('212: ',e)
        abort(400)

    #------------------------------------------------------------
    total_value = dict()
    for i in dataset:
        if isinstance(i, str):
            if 'static' in i:
                datasetvalue = dataset_check(str(i))

                try:

                    if period:
                        ## datestart: 2019-10-30, dateend: 2019-12-31
                        datasetdate = " where DATE(date) BETWEEN '%s' AND '%s'" % (datestart, dateend)
                        query = "select * from %s%s" % (datasetvalue, datasetdate)
                    else:
                        query = "select * from %s" % (datasetvalue)
                    #
                    # if datasetvalue == 'dataset_acc_inflow':
                    #     query = "select	date, dow as week, sum(in_flow) as flow from dataset_acc_inflow " + datasetdate + " group by date, dow order by date"
                    #
                    # # query = "select	date, dow as week, sum(in_flow) as flow from "+datasetvalue+" group by date, dow order by date limit 100"
                    # elif datasetvalue == 'dataset_acc_outflow':
                    #     query = "select	date, dow as week, sum(out_flow) as flow from dataset_acc_outflow " + datasetdate + " group by date, dow order by date"
                    records = dbsearch1.execute(query)

                    result = []

                    import operator

                    for row_n in records:
                        valueaa = []
                        key_count = 0
                        keyaa = []
                        for x, y in row_n.items():
                            print(x,y)
                            valueaa.extend([y])
                            if key_count == 0:
                                keyaa.extend([x])
                        key_count += 1

                        # row_n = [row_n]

                        # print(row_n)
                        # print(type(row_n))
                        # print(row_n[0])
                        # row_n[0] = str(item.get('date'))

                        # cc=str(cc).split(',')[0]
                        # print(type(cc))
                        result.append(valueaa)
                        # result.append(row_n)

                    result.insert(0, keyaa)
                    # print(result)

                    ss = {}
                    ss[i] = result
                    total_value.update(ss)

                except Exception as e:
                    print('272: ', e)
                    ss = {}
                    ss[str(i)] = None
                    total_value.update(ss)

            else:
                ss={}
                ss[str(i)] = None
                total_value.update(ss)

        else:
            ss = {}
            ss[str(i)] = None
            total_value.update(ss)

    # dataset_value = get_HYGAS_dataset_value(pkey, dataset, period_value)
    # print(total_value)
    kk={'dataset':total_value}
    return jsonify(kk)

'''
cjr-tourist: 관광객 현황

cjr-tourist-weekend: 주말
cjr-tourist-time-range: 시간대황
cjr-tourist-age: 연령대
cjr-tourist-gender: 성별
cjr-tourist-country: 국적별

cjr-spend: 소비 현황

cjr-spend-weekend: 주말별
cjr-spend-time-range: 시간대별
cjr-spend-age: 연령대
cjr-spend-country: 국적별
cjr-spend-gender: 성별
cjr-spend-category: 4대 관광

acc: 문화전당

acc-inflow
acc-outflow
'''
def dataset_check(dataset):
    dataset = dataset.replace('static/','').replace('-','_')
    if 'acc' in dataset:
        return 'dataset_'+dataset
    elif 'cjr-tourist' in dataset:
        return 'dataset_'+dataset
    elif 'cjr-spend' in dataset:
        return 'dataset_'+dataset
    else:
        return 'dataset_'+dataset



def get_HYGAS_dataset_value(pkey, dataset, period_value):
    result = list()
    for i in dataset:
        start_year = '%04d'%(period_value[0])
        start_date = '%04d%02d%02d' % (period_value[0], period_value[1], period_value[2])
        from API.Predict.get_data_class import get_train_model, get_predic_data
        get_class = get_predic_data()
        # result.append(get_class.get_Yearly_coming_5years_month('naju', int(start_year), int(start_date)))
        result.append(get_class.get_Yearly_coming_5years_month('naju', int(2019), int(20191006)))

    return result

def get_period_value(period):
    period = period.split('~')

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

        ## 년/월/일/시/분/초 6개가 나와야함.
        if len(valuecheck) != 6:
            ## 부족한 개수만큼 추가.
            aa = 0
            while(aa < 6-len(valuecheck)):
                value.append(int(0))
                aa += 1
    return value


####################################################

'''
from __init__ import app
import os
from flask import Flask, request, redirect, url_for
from flask import send_from_directory
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = ''
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # 파일이없다
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)

        # 파일네임이없다 ( .filename )
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)

        # 파일 가져오기 ( request.files['네임'] )
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 업로드 ( .save(경로) )
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))


# 파일이 허락된 형식인지검사
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 파일이 있는 경로로 이동시킴
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

'''