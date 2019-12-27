# -*- coding: utf-8 -*-
# predic_dedail set API

'''general'''
import json
import datetime
import os
import sys
import shutil
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
from DB.DataBase.models import Login, DataTable, LocationTable, ResourceTable
from API.api_helper.user_directory import folder_dataupload_path, folder_prediction_path
from API.api_helper.api_helper import response_json_value, response_json_list, post_request
import collections
from sqlalchemy import func
from DB.DataBase.machbase import connect
''' '''
from flask_cors import CORS
import tempfile

data_apis = Blueprint('data_upload_apis', __name__, url_prefix='/api')

@data_apis.route('/machtest', methods=['GET'])
def mach_test():

    # for i in range(2):
    #     kk = 96.1
    #     query1 = "insert into tag values('HYGAS.NAJU_C_HOUSE.30001.1', now, %f)"%(kk)
    #     dblist2 = connect(query1)

    query = "SELECT TIME, VALUE FROM tag where name='HYGAS.NAJU_C_HOUSE.30001.1'"
    dblist = connect(query)
    print(dblist)
    k = 0
    value_name = list()
    final_value = []
    for row_n in dblist:
        # print(row_n)
        # print(type(row_n))

        row_n['VALUE'] = float(row_n.get('VALUE'))
        # dict_value={}
        middle_value = []
        for x, y in row_n.items():
            if k == 0:
                value_name.append(x)
            # dict_value.update({x:y})
            middle_value.extend([y])
        final_value.append(middle_value)
        k += 1

    final_value.insert(0, value_name)
    return jsonify(final_value)

@data_apis.route('/attach', methods=['GET', 'POST'])
def file_attach():
    print("file_attach")
    if request.method == 'POST':

        now = datetime.datetime.now()
        nowDate = now.strftime('%Y%m%d')
        nowTime = now.strftime('%H%M%S')
        # strtime = 'temp_'+ nowDate + nowTime+'_'
        strtime = nowDate + nowTime + '_'
        file_list = list()

        if not os.path.isdir(folder_dataupload_path):
            os.mkdir(folder_dataupload_path)

        tempfilepath = folder_dataupload_path + 'tempfile/'

        if not os.path.isdir(tempfilepath):
            os.mkdir(tempfilepath)

        ## todo: 파일용량 제한 가능 -> app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
        for f in request.files.getlist('attach'):
            # print(f.filename)
            # print(secure_filename(strtime+f.filename))
            ## source_filename이 한글적용이 안되는 문제가 있어 제거.
            # f.save(folder_path3 + secure_filename(strtime+f.filename))
            f.save(tempfilepath + strtime + f.filename)
            file_list.append(strtime+f.filename)

        result = {"attach":file_list}

        return jsonify(result)
        # return jsonify(file_list)

@data_apis.route('/attach/<string:id>', methods=['DELETE'])
def file_delete(id):
    print(id)

    try:
        for name in [id]:
            tempfilepath = folder_dataupload_path + name
            print(tempfilepath)

            os.remove(tempfilepath)


        return jsonify(True)
    except:
        return jsonify(False)




@data_apis.route('/datasets', methods=['POST'])
def file_create():
    try:
        print("file_create")
        req = request.get_json()
        jsonString = json.dumps(req)
        data = json.loads(jsonString)
        # 한개만 받아올때 리스트 씌워서 작업.
        file_key = [data['attach']]

        try:
            area = data['location']
        except:
            ## todo: 사용자 입력에러(400) 리턴을 원할 경우 abort(400)으로 바꾸면됨.
            area = 1

        try:
            ## todo: resource 값에 따라 저장되는 모델용 폴더명 확인.
            resource = data['resource']
            # if resource == '13001.1':
            #     resource = 'insu'
            # elif resource == '30005.0':
            #     resource = 'sub'
            # elif resource =='3303.0':
            #     resource = 'temp'
            # else:
            #     resource = 'insu'
        except:
            ## resource 값이 없으면 insu 데이터 자원
            ## todo: 사용자 입력에러(400) 리턴을 원할 경우 abort(400)으로 바꾸면됨.
            resource = 2

        try:
            purpose = data['purpose']
        except:
            ## purpose 값이 없으면 예측으로.
            ## todo: 사용자 입력에러(400) 리턴을 원할 경우 abort(400)으로 바꾸면됨.
            purpose = 'prediction'

        # print("file_key: ",file_key)

        for name in file_key:
            tempfilepath = folder_dataupload_path + 'tempfile/' + name
            new_name = folder_dataupload_path + name

            try:
                # temp 에서 실 저장소로 이동.
                shutil.copy(tempfilepath, new_name)
                # print("name: ", name)
                # print("new_name: ", new_name)

                ## 파일 읽어서 년도 정보 2014 획득.
                ## 첫날짜, 마지막 날짜 DB에 저장.
                ##########################################################
                with open(new_name, 'r') as f:
                    date_get = f.readlines()
                # 파일 year 정보.
                date_start_value = date_get[1].split(' ')
                date_start_year = int(date_start_value[0])
                date_start_month = int(date_start_value[1])
                date_start_day = int(date_start_value[2])
                date_end_value = date_get[-1].split(' ')
                date_end_year = int(date_end_value[0])
                date_end_month = int(date_end_value[1])
                date_end_day = int(date_end_value[2])

                period = "%04d-%02d-%02d~%04d-%02d-%02d" % (
                date_start_year, date_start_month, date_start_day, date_end_year, date_end_month, date_end_day)

                ###########################################################
                ## /home/uk/PredictionServer/prediction/data/insu/naju_insu_2014
                ## 모델용에 맞춰 저장.

                try:
                    quer = db_session.query(ResourceTable.name,ResourceTable.id).filter(ResourceTable.key == resource)
                    records = db_session.execute(quer)
                    for i in records:
                        for x, y in i.items():
                            ## insu
                            if x == 'resource_name':
                                string_resource = y
                            ##30001.1
                            if x == 'resource_id':
                                mach_resource = y

                except:
                    ## resource 테이블 이외의 key 값을 받을 경우 key=2인 insu 값 기본으로.
                    ## todo: 사용자 입력에러(400) 리턴을 원할 경우 abort(400)으로 바꾸면됨.
                    string_resource = 'insu'
                    mach_resource = '30001.1'

                try:
                    quer = db_session.query(LocationTable.id).filter(LocationTable.key == area)
                    records = db_session.execute(quer)
                    for i in records:
                        ## 'naju
                        for x,y in i.items():
                            string_area = y
                except:
                    ## location 테이블 이외의 key 값을 받을 경우 기본 key=1인 naju 지역을 기본으로.
                    ## todo: 사용자 입력에러(400) 리턴을 원할 경우 abort(400)으로 바꾸면됨.
                    string_area = 'naju'

                # print("string_rr: ", string_resource)
                # print(mach_resource)
                # print(string_area)

                ## todo: resource에 따라 해당 폴더로 들어감. (폴더명과 변수명 일치 여부 확인)
                model_save_path = folder_prediction_path + "data/%s/%s_%s_%d" % (string_resource, string_area, string_resource, date_start_year)
                ## DB 모델용 저장 파일. (파일복사)
                ## shutil 사용.
                # print(model_save_path)
                shutil.copy(new_name,model_save_path)
                # print("model_s_path: ",model_save_path)

                # if resource == 'insu':
                #     resource = '30001.1'
                # elif resource == 'sub':
                #     resource = '30005.0'
                # elif resource == 'temp':
                #     resource = '3303.0'
                # else:
                #     resource = '30001.1'

                ## 마크 베이스 입력---------------------------
                machbase_input(new_name, string_area, mach_resource, date_start_year)
                ## 마크 베이스 입력 --------------------------

                ## HYGAS.NAJU.30001.1
                machbase_class_name = 'HYGAS.%s.%s'%(string_area.upper(), mach_resource)

                # print(period)
                # print(machbase_class_name)
                # print(new_name)
                # print(purpose)
                # print(resource)
                # print(area)
                # print(model_save_path)

                ## DB에 저장.
                db_session.add(DataTable(period=period, machbase_name=machbase_class_name, file_path=new_name, purpose=purpose, resource=resource, location=area, save_path=model_save_path))
                db_session.commit()

            except Exception as e:
                return jsonify(e)

        return jsonify(True)

    except Exception as e:
        return jsonify(False)


## ReadAll files info
@data_apis.route('/datasets', methods=['GET'])
def api_file_search():
    limit = request.args.get('limit', type=int)
    page = request.args.get('page', type=int)

    # query = "select * from data ORDER BY key"
    query = "select key, inserted, location, purpose, resource, period, file_path from data ORDER BY key"
    records = db_session.execute(query)

    count = db_session.query(func.count('*')).select_from(DataTable).scalar()

    result = []

    for i in records:
        # print(i)
        result_dict = dict()
        for x,y in i.items():
            # print(x,y)
            if x == 'file_path':
                x = 'fileKey'
                y = y.split('/')[-1]
                result_dict.update({x: y})
            elif x == 'location':
                query = "select id, key, name, name_en from location where key=%d" % (y)
                records1 = db_session.execute(query)
                location_result={}
                for location_i in records1:
                    location_result.update(dict(location_i))

                result_dict.update({x: location_result})
            elif x == 'resource':
                query = "select id, explain, key, name from resource where key=%d" % (y)
                records2 = db_session.execute(query)
                resource_result = {}
                for resource_i in records2:
                    resource_result.update(dict(resource_i))

                result_dict.update({x: resource_result})

            else:
                result_dict.update({x: y})
        # print(result_dict)

        result.append(result_dict)
        # print(result)

    fresult = {"dataset": result, "total": count}
    return jsonify(fresult)

# @data_apis.route('/datasets/statics', methods=['GET'])
# def smartCity_datasetlist():
#     print('---------------1----------')
#     dlist = [name for name in dbsearch1.table_names() if name.startswith('dataset_')]
#     result=list()
#     for i in dlist:
#         result.append("static/%s"%(i.replace("dataset_","")))
#
#     return jsonify({"resources": result})


# @data_apis.route('/datasets/staticstest', methods=['GET'])
# def smartCity_datasetlisttest():
#     dlist = [name for name in dbsearch1.table_names() if name.startswith('dataset_')]
#     result = list()
#     for i in dlist:
#         result.append("static/%s" % (i.replace("dataset_", "")))
#
#     # req = request.get_json()
#     # jsonString = json.dumps(req)
#     # data = json.loads(jsonString)
#
#     # datatable = data['resource']
#
#     total_value = dict()
#     total_value2 = list()
#
#     query = "select * from %s" % ('dataset_acc_inflow')
#
#     # if datasetvalue == 'dataset_acc_inflow':
#     #     query = "select	date, dow as week, sum(in_flow) as flow from dataset_acc_inflow " + datasetdate + " group by date, dow order by date"
#     #
#     # # query = "select	date, dow as week, sum(in_flow) as flow from "+datasetvalue+" group by date, dow order by date limit 100"
#     # elif datasetvalue == 'dataset_acc_outflow':
#     #     query = "select	date, dow as week, sum(out_flow) as flow from dataset_acc_outflow " + datasetdate + " group by date, dow order by date"
#     records = dbsearch1.execute(query)
#     result = []
#     for i in records:
#         # print(i)
#         result_dict = dict()
#         for x, y in i.items():
#             result_dict.update({x: y})
#         # print(result_dict)
#
#         result.append(result_dict)
#
#
#     return response_json_list(result)

## Read
@data_apis.route('/datasets/<int:key>', methods=['GET'])
def api_data_search(key):
    try:
        query = "select key, inserted, location, purpose, resource, period, file_path from data WHERE key =%d" % (key)
        records = db_session.execute(query)
        result = []
        for i in records:
            # print(i)
            result_dict = dict()
            for x, y in i.items():
                # print(x,y)
                if x == 'file_path':
                    x = 'fileKey'
                    y = y.split('/')[-1]
                    result_dict.update({x: y})
                elif x == 'location':
                    query = "select id, key, name, name_en from location where key=%d" % (y)
                    records1 = db_session.execute(query)
                    location_result = {}
                    for location_i in records1:
                        location_result.update(dict(location_i))

                    print(location_result)

                    result_dict.update({x: location_result})
                elif x == 'resource':
                    query = "select id, explain, key, name from resource where key=%d" % (y)
                    records2 = db_session.execute(query)
                    resource_result = {}
                    for resource_i in records2:
                        resource_result.update(dict(resource_i))

                    result_dict.update({x: resource_result})
                else:
                    result_dict.update({x: y})
            # print(result_dict)

            result.append(result_dict)

        return response_json_value(result)
    except:
        return jsonify(False)

## Delete
@data_apis.route('/datasets/<int:key>', methods=['DELETE'])
def api_data_delete(key):
    try:
        ## todo: 삭제시에 저장된 파일 같이 삭제.(fileupload)
        db_session.query(DataTable).filter(DataTable.key == key).delete()
        db_session.commit()
        return jsonify(True)
    except:
        return jsonify(False)

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
            "resource": "30001.1"
        }, {
            "source":" hygas",
            "location": "naju",
            "resource": "30001.2"
        }
	]
}
{
  "period":"2017-11-06 1 ~ 2017-12-30 1 ",
  "dataset": [
		"static/acc-inflow",
        "static/acc-outflow",
         {
            "source":" hygas",
            "location": 1,
            "resource": 2
        }, {
            "source":" hygas",
            "location": 1,
            "resource": 2
        }
	]
}
'''


@data_apis.route('/datasets/values', methods=['POST'])
def api_data_values():

    try:
        key = session['logger']
        key = db_session.query(Login.key).filter(Login.id == str(key))
        login = db_session.query(Login).get(key)
    except:
        key = 0
    else:
        key = login.key

    req = request.get_json()
    jsonString = json.dumps(req)
    data = json.loads(jsonString)

    try:
        dataset = data['dataset']
    except Exception as e:
        print('212: ',e)
        abort(400)


    try:
        period = data['period']
        ## 날짜시간 [2018, 3, 10, 1, 0, 0, 2019, 3, 6, 1, 0, 0] -> 리스트 len = 12
        period_value = get_period_value(str(period))
        # print(period_value)
        datestart = '%04d-%02d-%02d' % (period_value[0], period_value[1], period_value[2])
        dateend = '%04d-%02d-%02d' % (period_value[6], period_value[7], period_value[8])

    except:
        period = None

    #------------------------------------------------------------
    total_value = dict()
    total_value2 = list()
    meta_get = {}
    meta_get_list = list()
    for i in dataset:
        meta_get2 = []
        # print(i)

        ## 스마트시티 string #####################################################################
        if isinstance(i, str):
            if 'static' in i:
                datasetvalue = dataset_check(str(i))
                # print(period)

                try:
                    if period:
                        ## datestart: 2019-10-30, dateend: 2019-12-31
                        datasetdate = " where DATE(date) BETWEEN '%s' AND '%s'" % (datestart, dateend)
                        query = "select * from %s%s" % (datasetvalue, datasetdate)
                    else:
                        query = "select * from %s" % (datasetvalue)

                    print("query: ", query)
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

                        count += 1
                        key_count += 1

                        result.append(valueaa)
                        # result.append(row_n)

                    dateend = result[-1][0]
                    # print(dateend)

                    result.insert(0, keyaa)
                    # print(result)
                    # print("result: ",result)
                    ss = {}
                    ss[i] = result
                    total_value.update(ss)
                    total_value2.append(result)

                    meta_get2.append({"beginDate": datestart, "endDate":dateend})
                    meta_get.update({str(i): meta_get2})
                    meta_get_list.extend(meta_get2)
                    # print("meta_get: ",meta_get)

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

        ## 해양에너지 dict #####################################################################
        elif isinstance(i,dict):
            try:
                # argument = data['arguments']
                resource = i['resource']
                area = i['location']
                ## todo: 현재 폴더에 naju 데이터 뿐이기 때문에, 일단 테스트에서는 naju만 되게끔, 나중 지우면됨.
                if not area == 1:
                    area = 1
                '''
                "location": "naju",
                "resource": "30001.1"
                '''

                try:
                    # todo: 현재 resource(2,3)은 인수량,검침량으로 이 두개는 name=insu값을 가짐(검침량도 인수량으로 대체하라는 오더).
                    ## 그런데 나머지 resource(1,4)는 temp, sub 값을 가지는데, insu데이터와 파일 구조가 달라서 얻는 값들을 따로 정의 해줘야함.
                    ## 현재는 1,4도 name을 insu로 지정해 주겠음.
                    if resource == 1 or resource == 4:
                        resource = 2

                    quer = db_session.query(ResourceTable.name,ResourceTable.id).filter(ResourceTable.key == resource)
                    records = db_session.execute(quer)
                    for i in records:
                        for x, y in i.items():
                            ## insu
                            if x == 'resource_name':
                                string_resource = y
                            ##30001.1
                            if x == 'resource_id':
                                mach_resource = y

                    print(string_resource)
                    print(mach_resource)

                except:
                    ## resource(1,2,3,4)를 제외한 값도 일단은 가장 기본 값인 resource(1)의  insu, 30001.1 지정.
                    string_resource = 'insu'
                    mach_resource = '30001.1'

                try:
                    quer = db_session.query(LocationTable.id).filter(LocationTable.key == area)
                    records = db_session.execute(quer)
                    for i in records:
                        ## 'naju
                        for x,y in i.items():
                            string_area = y
                except:
                    string_area = 'naju'

                try:
                    source = i['source']
                except:
                    source = 'HYGAS'

                if not period:
                    ## todo: 현재있는 data/insu의 파일내용 모두 출력인데, 나중에 기간에 따라 출력 바뀌게 될시 여기 수정.
                    datelist = []
                    import glob
                    ## 저장된 데이터셋 개수(filecountvalue) , 가장작은 년도(file_start_year), filelist리스트=[2014,2015, .. ,2019]
                    filecount = folder_prediction_path + 'data/%s/' % (string_resource)
                    filecountvalue = len(glob.glob1(filecount, "%s_%s*"%(string_area,string_resource)))
                    file_start_year = sorted(glob.glob1(filecount, "%s_%s*"%(string_area,string_resource)))[0]
                    file_start_year = int(file_start_year.split("_")[-1])
                    # for i in range(dateend - datestart + 1):
                    ## range=6 (2014_2019)
                    for i in range(filecountvalue):
                        datelist.append(file_start_year)
                        file_start_year += 1
                else:
                    ## 해양도시 insu값 무조건 다 출력.
                    # datestart_hy = 2014
                    # dateend_hy = 2019
                    # print(datestart)
                    datelist = []
                    import glob
                    ## 저장된 데이터셋 개수(filecountvalue) , 가장작은 년도(file_start_year), filelist리스트=[2014,2015, .. ,2019]
                    filecount = folder_prediction_path + 'data/%s/' % (string_resource)
                    filecountvalue = len(glob.glob1(filecount, "%s_%s*" % (string_area, string_resource)))
                    file_start_year = sorted(glob.glob1(filecount, "%s_%s*" % (string_area, string_resource)))[0]
                    file_start_year = int(file_start_year.split("_")[-1])
                    # for i in range(dateend - datestart + 1):
                    ## range=6 (2014_2019)
                    for i in range(filecountvalue):
                        datelist.append(file_start_year)
                        file_start_year += 1


            except Exception as e:
                print(e)
                return abort(400)

                # pandas->csv 파일로 가져왔을때, 문제가 있는거 같다. 같은 값인데, 에러가 난다. open()으로 읽어서 처리.
            else:
                dataname = str()
                # print(resource.count('.'))
                if mach_resource.count('.') == 1:
                    final_value_list = []
                    # print("datelist: ",datelist)
                    for ddstart in datelist:

                        # print("ddstart: ",ddstart)

                        path = folder_prediction_path + 'data/%s/%s_%s_%d' % (string_resource, string_area.lower(), string_resource, ddstart)
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
                # meta_get.update({str(source).upper() + '.' + str(resource): meta_get2})
                meta_get_list.extend(meta_get2)

            # total_value.update({str(source).upper()+'.'+str(resource):final_value_list})
            total_value2.append(final_value_list)

        else:
            # ss = {}
            # ss[str(i)] = None
            # total_value.update(ss)
            total_value2.append([])
            meta_get_list.append([])


        # meta = {}
        # meta["meta"] = meta_get

        # total_value.update(meta)


    # dataset_value = get_HYGAS_dataset_value(key, dataset, period_value)

    # kk={'dataset':total_value}
    # kk.update(meta)

    final_json_value={"dataset":total_value2,"meta":meta_get_list}

    # kk = {}
    # kk['datasets'] = total_value
    # total_value.update(kk)
    # print(total_value)
    return jsonify(final_json_value)

@data_apis.route('/analysis', methods=['POST'])
def api_analysis():
    try:
        key = session['logger']
        key = db_session.query(Login.key).filter(Login.id == str(key))
        login = db_session.query(Login).get(key)
    except:
        key = 0
    else:
        key = login.key

    req = request.get_json()
    jsonString = json.dumps(req)
    data = json.loads(jsonString)

    try:
        dataset = data['dataset']
    except Exception as e:
        print('212: ',e)
        abort(400)


    try:
        period = data['period']
        ## 날짜시간 [2018, 3, 10, 1, 0, 0, 2019, 3, 6, 1, 0, 0] -> 리스트 len = 12
        period_value = get_period_value(str(period))
        # print(period_value)
        datestart = '%04d-%02d-%02d' % (period_value[0], period_value[1], period_value[2])
        dateend = '%04d-%02d-%02d' % (period_value[6], period_value[7], period_value[8])

    except:
        period = None

    #------------------------------------------------------------
    total_value = dict()
    total_value2 = list()
    meta_get = {}
    meta_get_list = list()
    for i in dataset:
        meta_get2 = []
        # print(i)

        ## 스마트시티 string #####################################################################
        if isinstance(i, str):
            if 'static' in i:
                datasetvalue = dataset_check(str(i))
                # print(period)

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

                        count += 1
                        key_count += 1

                        result.append(valueaa)
                        # result.append(row_n)

                    dateend = result[-1][0]
                    # print(dateend)

                    result.insert(0, keyaa)
                    # print(result)
                    # print("result: ",result)
                    ss = {}
                    ss[i] = result
                    total_value.update(ss)
                    total_value2.append(result)

                    meta_get2.append({"beginDate": datestart, "endDate":dateend})
                    meta_get.update({str(i): meta_get2})
                    meta_get_list.extend(meta_get2)
                    # print("meta_get: ",meta_get)

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

        ## 해양에너지 dict #####################################################################
        elif isinstance(i,dict):
            try:
                # argument = data['arguments']
                resource = i['resource']
                area = i['location']
                ## 지역이 나주가 아니면 naju로 강제 변환.
                # if not area == 'naju':
                #     area = 'naju'
                '''
                "location": "naju",
                "resource": "30001.1"
                '''

                try:
                    quer = db_session.query(ResourceTable.name,ResourceTable.id).filter(ResourceTable.key == resource)
                    records = db_session.execute(quer)
                    for i in records:
                        for x, y in i.items():
                            ## insu
                            if x == 'resource_name':
                                string_resource = y
                            ##30001.1
                            if x == 'resource_id':
                                mach_resource = y
                except:
                    string_resource = 'insu'
                    mach_resource = '30001.1'

                try:
                    quer = db_session.query(LocationTable.id).filter(LocationTable.key == area)
                    records = db_session.execute(quer)
                    for i in records:
                        ## 'naju
                        for x,y in i.items():
                            string_area = y
                except:
                    string_area = 'naju'


                try:
                    source = i['source']
                except:
                    source = 'HYGAS'

                if not period:
                    ## todo: 현재있는 data/insu의 파일내용 모두 출력인데, 나중에 기간에 따라 출력 바뀌게 될시 여기 수정.
                    datelist = []
                    import glob
                    ## 저장된 데이터셋 개수(filecountvalue) , 가장작은 년도(file_start_year), filelist리스트=[2014,2015, .. ,2019]
                    filecount = folder_prediction_path + 'data/%s/' % (string_resource)
                    filecountvalue = len(glob.glob1(filecount, "%s_%s*"%(string_area,string_resource)))
                    file_start_year = sorted(glob.glob1(filecount, "%s_%s*"%(string_area,string_resource)))[0]
                    file_start_year = int(file_start_year.split("_")[-1])
                    # for i in range(dateend - datestart + 1):
                    ## range=6 (2014_2019)
                    for i in range(filecountvalue):
                        datelist.append(file_start_year)
                        file_start_year += 1
                else:
                    ## 해양도시 insu값 무조건 다 출력.
                    # datestart_hy = 2014
                    # dateend_hy = 2019
                    # print(datestart)
                    datelist = []
                    import glob
                    ## 저장된 데이터셋 개수(filecountvalue) , 가장작은 년도(file_start_year), filelist리스트=[2014,2015, .. ,2019]
                    filecount = folder_prediction_path + 'data/%s/' % (string_resource)
                    filecountvalue = len(glob.glob1(filecount, "%s_%s*" % (string_area, string_resource)))
                    file_start_year = sorted(glob.glob1(filecount, "%s_%s*" % (string_area, string_resource)))[0]
                    file_start_year = int(file_start_year.split("_")[-1])
                    # for i in range(dateend - datestart + 1):
                    ## range=6 (2014_2019)
                    for i in range(filecountvalue):
                        datelist.append(file_start_year)
                        file_start_year += 1


            except Exception as e:
                print(e)
                return abort(400)


                # todo: csv 파일로 가져왔을때, 문제가 있는거 같다. 같은 값인데, 에러가 난다.
            else:
                dataname = str()
                # print(resource.count('.'))
                if mach_resource.count('.') == 1:
                    final_value_list = []
                    # print("datelist: ",datelist)
                    for ddstart in datelist:

                        # print("ddstart: ",ddstart)

                        path = folder_prediction_path + 'data/%s/%s_%s_%d' % (string_resource, string_area.lower(), string_resource, ddstart)
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
                # meta_get.update({str(source).upper() + '.' + str(resource): meta_get2})
                meta_get_list.extend(meta_get2)

            # total_value.update({str(source).upper()+'.'+str(resource):final_value_list})
            total_value2.append(final_value_list)

        else:
            # ss = {}
            # ss[str(i)] = None
            # total_value.update(ss)
            total_value2.append([])
            meta_get_list.append([])


        # meta = {}
        # meta["meta"] = meta_get

        # total_value.update(meta)


    # dataset_value = get_HYGAS_dataset_value(key, dataset, period_value)

    # kk={'dataset':total_value}
    # kk.update(meta)

    final_json_value={"dataset":total_value2,"meta":meta_get_list}

    # kk = {}
    # kk['datasets'] = total_value
    # total_value.update(kk)
    # print(total_value)
    return jsonify(final_json_value)

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



def get_HYGAS_dataset_value(key, dataset, period_value):
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

def machbase_input(path, area, resource, startyear):
    final_value_list = list()
    # folder_path = '/home/uk/PredictionServer/prediction/prediction_ETRI/'
    # path = folder_path + 'data/insu/%s_insu_%d' % (area.lower(), ddstart)
    # area = 'naju'
    # resource = 'insu'  # or '30001.1
    # ddstart = startyear

    # print("path: ", path)

    with open(path, 'r') as f:
        dataname_get = f.readlines()

    # print("dataname_get: ",dataname_get)
    # date_name = dataname_get[0].replace('\t', ' ').split(' ')
    # print("date_name: ", date_name)

    mach_usekind = list()
    resource_value = str()

    # todo: csv 파일 컬럼은 반듯이 년, 월, 일, house ...로 *년,월,일 꼭 있어야함*
    count = 0
    for ii in dataname_get:
        if count == 0:
            date_name = ii.replace('\t', ' ').split(' ')
            for i in date_name:
                if '_' in i:
                    ## strip = 뒤 \n 제거
                    i = i.split('_')[1].strip().upper()

                    # print(resource)
                    # print(mach_usekind)
                mach_usekind.append(i)

            ## 년/원/일 을 제외한 뒤에 나머지 컬럼명을 가져옴.
            mach_usekind = mach_usekind[3:]
            # print(mach_usekind)
            ## 이미 받아올때 30001.1로 받아올듯.
            # if resource == 'insu':
            #     resource_value = '30001.1'
            # else:
            #     resource_value = '30001.2'

            try:
                ## 1. 해당 테크 테이블 만들고.
                ## insert into tag metadata values ('TAG_0001');
                for t in mach_usekind:
                    query = "insert into tag metadata values ('HYGAS.%s_C_%s.%s')" % (area.upper(), t, resource_value)
                    # print(query)
                    ## todo: 아래 주석 해제.
                    # dblist = connect(query)
                    # print(dblist)
            except:
                pass

        else:
            k = 0
            for usekind in mach_usekind:
                date = ii.replace('\t', ' ').split(' ')[0:3]
                date_value = '%d-%02d-%02d' % (int(date[0]), int(date[1]), int(date[2]))
                # print(date_value)

                ## 3~14 (12걔)
                value = ii.replace('\t', ' ').split(' ')[3 + k]
                # print(value)
                ## 2. 정보 입력.
                query1 = "insert into tag values('HYGAS.%s_C_%s.%s', '%s', %d)" % (
                area.upper(), usekind, resource_value, date_value, int(value))
                # print(query1)
                ## todo: 아래 주석 해제.
                # dblist2 = connect(query1)
                # print(dblist2)
                k += 1

        count += 1


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