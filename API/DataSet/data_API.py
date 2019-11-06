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

@data_apis.route('/file', methods=['POST', 'GET'])
def file_creaaawte():


    if request.headers['Content-Type'] == 'text/plain':
        print(request.headers)

    return jsonify(True)

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

'''
HYGAS.NAJU_C_HOUSE.30001.1 - 나주_하우스_가스인수량.
HYGAS.NAJU_C_HOUSE.30001.2 - 나주_하우스_가스검침량.
{
        "period": "2019-11-01 10:23:45~2019-11-30 23:59:59",
        "dataset": [
                                "NAJU.30001.1"
        ]
}
'''
## Readall
@data_apis.route('/datasets', methods=['GET','POST'])
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
        print(period_value)
        # datestart = '%04d-%02d-%02d' % (period_value[0], period_value[1], period_value[2])
        # dateend = '%04d-%02d-%02d' % (period_value[6], period_value[7], period_value[8])
        datestart = '%04d' % (period_value[0])
    except:
        period = None

    try:
        dataset = data['dataset']
    except Exception as e:
        print('212: ',e)
        abort(400)
    final_result = dict()
    final_result2 = dict()
    for data in dataset:

        try:
            argument = data['arguments']
            resource = argument['resource']
            area = argument['location']

            ## 지역이 나주가 아니면 naju로 강제 변환.
            if not area == 'naju':
                area = 'naju'

        except Exception as e:
            print(e)
            return abort(400)

        else:
            print(resource.count('.'))
            if resource.count('.') == 1:
                path = folder_path + 'data/insu/%s_insu_%s' % (area.lower(), datestart)
                print(path)

                ## '/home/uk/PredictionServer/prediction/prediction_ETRI/data/insu/naju_insu_2019'
                with open(path, 'r') as f:
                    dataname = f.readline().strip()
                    dataname = dataname.replace('\t', ' ')
                    dataname = dataname.split(" ")[3:]
                    # print(dataname)

            pddata = pd.read_csv(path, delim_whitespace=True)
            data1 = "year month date"

            for index, row in sorted(pddata.iterrows()):
                datavalue1 = []
                # datavalue1_str = str()
                for i in data1.split(" "):
                    datavalue1.append(row[i])

                datavalue1_str = '%04d-%02d-%02d' % (datavalue1[0], datavalue1[1], datavalue1[2])

                datavalue2 = []
                for i in dataname:
                    datavalue2.append(row[i])

                # print(datavalue2)
                # temp_list = [date]

                M = dict(zip(dataname, datavalue2))
                L = {datavalue1_str: M}
                final_result.update(L)

            print(final_result)
            from API.DataSet.data_insu import data_insu
            final_result = data_insu(datestart)

            ss = {}
            ss[str(area).upper()+'.'+str(resource)] = final_result
            final_result2.update(ss)

        return jsonify(final_result2)

## Read
@data_apis.route('/datasets/<int:pkey>', methods=['GET'])
def api_data_search(pkey):
    pass


## Delete
@data_apis.route('/datasets/<int:pkey>', methods=['DELETE'])
def api_data_delete(pkey):
    pass

@data_apis.route('/dataset/dbtest', methods=['GET'])
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
        1
	]
}
'''


@data_apis.route('/dataset/values', methods=['POST'])
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
                    print(e)
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
    print(total_value)
    print(type(total_value))
    kk={'dataset':total_value}

    # kk = {}
    # kk['datasets'] = total_value
    # total_value.update(kk)
    # print(total_value)
    return jsonify(kk)

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