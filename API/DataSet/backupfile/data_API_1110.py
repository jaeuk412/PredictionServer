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
        dateend = int('%04d' % (period_value[6]))
        datestart = int('%04d' % (period_value[0]))

        datelist = []
        for i in range(dateend - datestart + 1):
            datestart += i
            datelist.append(datestart)

    except:
        period = None

    try:
        dataset = data['dataset']
    except Exception as e:
        print('212: ',e)
        abort(400)

    final_result2 = dict()
    meta_get = {}
    # print(dataset)
    for data in dataset:

        # print("data: ",data)

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
# todo: csv 파일로 가져왔을때, 문제가 있는거 같다. 같은 값인데, 에러가 난다.
        else:
            dataname = str()
            # print(resource.count('.'))
            if resource.count('.') == 1:
                final_value_list=[]
                for ddstart in datelist:
                    final_result = dict()
                    path = folder_path + 'data/insu/%s_insu_%d' % (area.lower(), ddstart)
                    print(path)
                    dataname = 'insu_sum'
                    ## '/home/uk/PredictionServer/prediction/prediction_ETRI/data/insu/naju_insu_2019'
                    # with open(path, 'r') as f:
                    #     dataname_get = f.readline().strip()

                    with open(path, 'r') as f:
                        dataname_get = f.readlines()

                    data_t = []
                    for ii in dataname_get:
                        data_t.append(ii[:-1].replace('\t',' '))

                    dataname_get = dataname_get[0].replace('\t', ' ')
                    dataname_get = dataname_get.split(" ")[3:]

                    print('0000290')
                    print(data_t[0])

                    print(dataname_get)

                    for k in dataname_get:
                        if k.split('_')[1].upper() in resource.split('_'):
                            dataname = [k]

                    print(dataname)

                    pddata = pd.read_csv(path, delim_whitespace=True)
                    data1 = "year month date"
                    total_value = 0
                    value_list = []
                    monthcheck = 1
                    for index, row in sorted(pddata.iterrows()):

                        yearmonthday = []
                        # datavalue1_str = str()

                        ## 각 날짜에 대한 년,월,일 값 가져옴.
                        for i in data1.split(" "):
                            yearmonthday.append(row[i])

                        yearmonthday_str = '%04d-%02d-%02d' % (yearmonthday[0], yearmonthday[1], yearmonthday[2])

                        file_datavalue = {}

                        for i in dataname:
                            if yearmonthday[1] == monthcheck:
                                total_value += row[i]
                            else:
                                value_list.append({monthcheck:total_value})
                                monthcheck = yearmonthday[1]
                                total_value = 0
                            # file_datavalue.update({i: row[i]})

                    print(value_list)
                    final_value_list.append({ddstart:value_list})

                print(final_value_list)
                return jsonify(final_value_list)


                    # print(final_result)

                    # tqq = []
                    # # final_result = {'2019-03-12': {'insu_houseJHeating': 20191, 'insu_house': 4068, 'insu_CNG': 16037, 'insu_bizHeating': 4226, 'insu_salesTwo': 388, 'insu_houseCooking': 1099, 'insu_heatFacility': 36946, 'insu_houseCHeating': 0, 'insu_sum': 201796, 'insu_salesOne': 5697, 'insu_bizCooling': 0, 'insu_heatCombined': 17, 'insu_industry': 113129}, '2019-02-14': {'insu_houseJHeating': 37582, 'insu_house': 6869, 'insu_CNG': 17381, 'insu_bizHeating': 7141, 'insu_salesTwo': 602, 'insu_houseCooking': 1192, 'insu_heatFacility': 58595, 'insu_houseCHeating': 0, 'insu_sum': 259550, 'insu_salesOne': 7724, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 122465}, '2019-06-24': {'insu_houseJHeating': 5141, 'insu_house': 576, 'insu_CNG': 19229, 'insu_bizHeating': 749, 'insu_salesTwo': 219, 'insu_houseCooking': 1261, 'insu_heatFacility': 17412, 'insu_houseCHeating': 0, 'insu_sum': 169024, 'insu_salesOne': 4354, 'insu_bizCooling': 1322, 'insu_heatCombined': 17, 'insu_industry': 118743}, '2019-05-10': {'insu_houseJHeating': 10866, 'insu_house': 1748, 'insu_CNG': 21136, 'insu_bizHeating': 1170, 'insu_salesTwo': 308, 'insu_houseCooking': 1286, 'insu_heatFacility': 24411, 'insu_houseCHeating': 0, 'insu_sum': 222303, 'insu_salesOne': 5363, 'insu_bizCooling': 566, 'insu_heatCombined': 35, 'insu_industry': 155414}, '2019-09-24': {'insu_houseJHeating': 2617, 'insu_house': 459, 'insu_CNG': 12490, 'insu_bizHeating': 271, 'insu_salesTwo': 159, 'insu_houseCooking': 787, 'insu_heatFacility': 11413, 'insu_houseCHeating': 0, 'insu_sum': 102277, 'insu_salesOne': 1840, 'insu_bizCooling': 544, 'insu_heatCombined': 30, 'insu_industry': 71665}, '2019-06-02': {'insu_houseJHeating': 5194, 'insu_house': 617, 'insu_CNG': 16815, 'insu_bizHeating': 601, 'insu_salesTwo': 171, 'insu_houseCooking': 852, 'insu_heatFacility': 15225, 'insu_houseCHeating': 0, 'insu_sum': 147798, 'insu_salesOne': 3427, 'insu_bizCooling': 1050, 'insu_heatCombined': 15, 'insu_industry': 103831}, '2019-08-30': {'insu_houseJHeating': 4605, 'insu_house': 571, 'insu_CNG': 29356, 'insu_bizHeating': 689, 'insu_salesTwo': 414, 'insu_houseCooking': 1660, 'insu_heatFacility': 31578, 'insu_houseCHeating': 0, 'insu_sum': 250917, 'insu_salesOne': 5165, 'insu_bizCooling': 2518, 'insu_heatCombined': 16980, 'insu_industry': 157380}, '2019-04-14': {'insu_houseJHeating': 14456, 'insu_house': 2101, 'insu_CNG': 19071, 'insu_bizHeating': 2603, 'insu_salesTwo': 328, 'insu_houseCooking': 1169, 'insu_heatFacility': 30133, 'insu_houseCHeating': 0, 'insu_sum': 212901, 'insu_salesOne': 5790, 'insu_bizCooling': 0, 'insu_heatCombined': 43, 'insu_industry': 137208}, '2019-03-28': {'insu_houseJHeating': 17874, 'insu_house': 2859, 'insu_CNG': 14435, 'insu_bizHeating': 4037, 'insu_salesTwo': 348, 'insu_houseCooking': 988, 'insu_heatFacility': 33255, 'insu_houseCHeating': 0, 'insu_sum': 181641, 'insu_salesOne': 6001, 'insu_bizCooling': 0, 'insu_heatCombined': 16, 'insu_industry': 101829}, '2019-07-24': {'insu_houseJHeating': 3291, 'insu_house': 358, 'insu_CNG': 18092, 'insu_bizHeating': 457, 'insu_salesTwo': 158, 'insu_houseCooking': 1063, 'insu_heatFacility': 20201, 'insu_houseCHeating': 0, 'insu_sum': 149164, 'insu_salesOne': 3673, 'insu_bizCooling': 2006, 'insu_heatCombined': 11, 'insu_industry': 99853}, '2019-07-13': {'insu_houseJHeating': 4786, 'insu_house': 589, 'insu_CNG': 24522, 'insu_bizHeating': 600, 'insu_salesTwo': 224, 'insu_houseCooking': 1452, 'insu_heatFacility': 27380, 'insu_houseCHeating': 0, 'insu_sum': 202173, 'insu_salesOne': 4648, 'insu_bizCooling': 2618, 'insu_heatCombined': 15, 'insu_industry': 135339}, '2019-05-09': {'insu_houseJHeating': 8696, 'insu_house': 1405, 'insu_CNG': 16839, 'insu_bizHeating': 931, 'insu_salesTwo': 245, 'insu_houseCooking': 985, 'insu_heatFacility': 19447, 'insu_houseCHeating': 0, 'insu_sum': 177103, 'insu_salesOne': 4263, 'insu_bizCooling': 451, 'insu_heatCombined': 28, 'insu_industry': 123814}, '2019-07-06': {'insu_houseJHeating': 3692, 'insu_house': 447, 'insu_CNG': 17861, 'insu_bizHeating': 420, 'insu_salesTwo': 157, 'insu_houseCooking': 1041, 'insu_heatFacility': 19943, 'insu_houseCHeating': 0, 'insu_sum': 147260, 'insu_salesOne': 3278, 'insu_bizCooling': 1831, 'insu_heatCombined': 11, 'insu_industry': 98579}, '2019-05-31': {'insu_houseJHeating': 10376, 'insu_house': 1196, 'insu_CNG': 22515, 'insu_bizHeating': 1133, 'insu_salesTwo': 331, 'insu_houseCooking': 1363, 'insu_heatFacility': 26003, 'insu_houseCHeating': 0, 'insu_sum': 236799, 'insu_salesOne': 6616, 'insu_bizCooling': 1683, 'insu_heatCombined': 24, 'insu_industry': 165560}, '2019-03-27': {'insu_houseJHeating': 22523, 'insu_house': 3565, 'insu_CNG': 18204, 'insu_bizHeating': 5172, 'insu_salesTwo': 438, 'insu_houseCooking': 1246, 'insu_heatFacility': 41940, 'insu_houseCHeating': 0, 'insu_sum': 229076, 'insu_salesOne': 7545, 'insu_bizCooling': 0, 'insu_heatCombined': 20, 'insu_industry': 128422}, '2019-09-16': {'insu_houseJHeating': 3780, 'insu_house': 498, 'insu_CNG': 18020, 'insu_bizHeating': 414, 'insu_salesTwo': 237, 'insu_houseCooking': 1136, 'insu_heatFacility': 16466, 'insu_houseCHeating': 0, 'insu_sum': 147556, 'insu_salesOne': 2741, 'insu_bizCooling': 829, 'insu_heatCombined': 43, 'insu_industry': 103392}, '2019-02-04': {'insu_houseJHeating': 46379, 'insu_house': 8749, 'insu_CNG': 21459, 'insu_bizHeating': 8805, 'insu_salesTwo': 753, 'insu_houseCooking': 1398, 'insu_heatFacility': 72344, 'insu_houseCHeating': 0, 'insu_sum': 320455, 'insu_salesOne': 9366, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 151202}, '2019-08-10': {'insu_houseJHeating': 3105, 'insu_house': 371, 'insu_CNG': 21300, 'insu_bizHeating': 381, 'insu_salesTwo': 272, 'insu_houseCooking': 1208, 'insu_heatFacility': 22913, 'insu_houseCHeating': 0, 'insu_sum': 182064, 'insu_salesOne': 3637, 'insu_bizCooling': 2378, 'insu_heatCombined': 12302, 'insu_industry': 114194}, '2019-01-03': {'insu_houseJHeating': 44912, 'insu_house': 7728, 'insu_CNG': 20207, 'insu_bizHeating': 9122, 'insu_salesTwo': 710, 'insu_houseCooking': 1254, 'insu_heatFacility': 65702, 'insu_houseCHeating': 0, 'insu_sum': 319288, 'insu_salesOne': 9530, 'insu_bizCooling': 0, 'insu_heatCombined': 4, 'insu_industry': 160120}, '2019-05-25': {'insu_houseJHeating': 7436, 'insu_house': 851, 'insu_CNG': 15572, 'insu_bizHeating': 956, 'insu_salesTwo': 268, 'insu_houseCooking': 944, 'insu_heatFacility': 17984, 'insu_houseCHeating': 0, 'insu_sum': 163777, 'insu_salesOne': 4748, 'insu_bizCooling': 495, 'insu_heatCombined': 26, 'insu_industry': 114498}, '2019-10-04': {'insu_houseJHeating': 9215, 'insu_house': 1580, 'insu_CNG': 15287, 'insu_bizHeating': 2250, 'insu_salesTwo': 541, 'insu_houseCooking': 1197, 'insu_heatFacility': 18717, 'insu_houseCHeating': 0, 'insu_sum': 160533, 'insu_salesOne': 6289, 'insu_bizCooling': 0, 'insu_heatCombined': 47, 'insu_industry': 105411}, '2019-04-30': {'insu_houseJHeating': 11144, 'insu_house': 1556, 'insu_CNG': 14911, 'insu_bizHeating': 2025, 'insu_salesTwo': 279, 'insu_houseCooking': 915, 'insu_heatFacility': 23560, 'insu_houseCHeating': 0, 'insu_sum': 166459, 'insu_salesOne': 4765, 'insu_bizCooling': 0, 'insu_heatCombined': 26, 'insu_industry': 107277}, '2019-07-11': {'insu_houseJHeating': 3734, 'insu_house': 475, 'insu_CNG': 18677, 'insu_bizHeating': 446, 'insu_salesTwo': 167, 'insu_houseCooking': 1106, 'insu_heatFacility': 20855, 'insu_houseCHeating': 0, 'insu_sum': 153988, 'insu_salesOne': 3486, 'insu_bizCooling': 1948, 'insu_heatCombined': 11, 'insu_industry': 103083}, '2019-06-01': {'insu_houseJHeating': 6160, 'insu_house': 730, 'insu_CNG': 19906, 'insu_bizHeating': 710, 'insu_salesTwo': 202, 'insu_houseCooking': 1008, 'insu_heatFacility': 18024, 'insu_houseCHeating': 0, 'insu_sum': 174967, 'insu_salesOne': 4051, 'insu_bizCooling': 1241, 'insu_heatCombined': 18, 'insu_industry': 122918}, '2019-09-06': {'insu_houseJHeating': 4479, 'insu_house': 502, 'insu_CNG': 25317, 'insu_bizHeating': 715, 'insu_salesTwo': 412, 'insu_houseCooking': 1408, 'insu_heatFacility': 23134, 'insu_houseCHeating': 0, 'insu_sum': 207309, 'insu_salesOne': 4662, 'insu_bizCooling': 1439, 'insu_heatCombined': 61, 'insu_industry': 145182}, '2019-04-15': {'insu_houseJHeating': 14640, 'insu_house': 2130, 'insu_CNG': 19323, 'insu_bizHeating': 2639, 'insu_salesTwo': 332, 'insu_houseCooking': 1184, 'insu_heatFacility': 30531, 'insu_houseCHeating': 0, 'insu_sum': 215715, 'insu_salesOne': 5870, 'insu_bizCooling': 0, 'insu_heatCombined': 44, 'insu_industry': 139021}, '2019-07-25': {'insu_houseJHeating': 3973, 'insu_house': 432, 'insu_CNG': 21839, 'insu_bizHeating': 552, 'insu_salesTwo': 191, 'insu_houseCooking': 1283, 'insu_heatFacility': 24385, 'insu_houseCHeating': 0, 'insu_sum': 180060, 'insu_salesOne': 4434, 'insu_bizCooling': 2422, 'insu_heatCombined': 13, 'insu_industry': 120536}, '2019-07-10': {'insu_houseJHeating': 3566, 'insu_house': 456, 'insu_CNG': 17843, 'insu_bizHeating': 426, 'insu_salesTwo': 159, 'insu_houseCooking': 1057, 'insu_heatFacility': 19923, 'insu_houseCHeating': 0, 'insu_sum': 147111, 'insu_salesOne': 3330, 'insu_bizCooling': 1861, 'insu_heatCombined': 11, 'insu_industry': 98479}, '2019-01-05': {'insu_houseJHeating': 41903, 'insu_house': 7423, 'insu_CNG': 18945, 'insu_bizHeating': 8531, 'insu_salesTwo': 666, 'insu_houseCooking': 1238, 'insu_heatFacility': 61599, 'insu_houseCHeating': 0, 'insu_sum': 299349, 'insu_salesOne': 8921, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 150120}, '2019-10-01': {'insu_houseJHeating': 8697, 'insu_house': 1507, 'insu_CNG': 14629, 'insu_bizHeating': 2175, 'insu_salesTwo': 523, 'insu_houseCooking': 1183, 'insu_heatFacility': 17912, 'insu_houseCHeating': 0, 'insu_sum': 153622, 'insu_salesOne': 6080, 'insu_bizCooling': 0, 'insu_heatCombined': 45, 'insu_industry': 100873}, '2019-03-14': {'insu_houseJHeating': 21553, 'insu_house': 3954, 'insu_CNG': 17568, 'insu_bizHeating': 5007, 'insu_salesTwo': 410, 'insu_houseCooking': 1203, 'insu_heatFacility': 40474, 'insu_houseCHeating': 0, 'insu_sum': 221067, 'insu_salesOne': 6948, 'insu_bizCooling': 0, 'insu_heatCombined': 19, 'insu_industry': 123932}, '2019-01-12': {'insu_houseJHeating': 42129, 'insu_house': 7609, 'insu_CNG': 19175, 'insu_bizHeating': 8663, 'insu_salesTwo': 676, 'insu_houseCooking': 1348, 'insu_heatFacility': 62345, 'insu_houseCHeating': 0, 'insu_sum': 302973, 'insu_salesOne': 9087, 'insu_bizCooling': 0, 'insu_heatCombined': 4, 'insu_industry': 151938}, '2019-05-21': {'insu_houseJHeating': 7908, 'insu_house': 890, 'insu_CNG': 16522, 'insu_bizHeating': 1016, 'insu_salesTwo': 285, 'insu_houseCooking': 1003, 'insu_heatFacility': 19082, 'insu_houseCHeating': 0, 'insu_sum': 173774, 'insu_salesOne': 5043, 'insu_bizCooling': 511, 'insu_heatCombined': 27, 'insu_industry': 121487}, '2019-07-08': {'insu_houseJHeating': 3941, 'insu_house': 492, 'insu_CNG': 19416, 'insu_bizHeating': 462, 'insu_salesTwo': 173, 'insu_houseCooking': 1118, 'insu_heatFacility': 21679, 'insu_houseCHeating': 0, 'insu_sum': 160076, 'insu_salesOne': 3609, 'insu_bizCooling': 2017, 'insu_heatCombined': 12, 'insu_industry': 107158}, '2019-01-25': {'insu_houseJHeating': 45927, 'insu_house': 8726, 'insu_CNG': 20889, 'insu_bizHeating': 9301, 'insu_salesTwo': 751, 'insu_houseCooking': 1464, 'insu_heatFacility': 67919, 'insu_houseCHeating': 0, 'insu_sum': 330058, 'insu_salesOne': 9556, 'insu_bizCooling': 0, 'insu_heatCombined': 4, 'insu_industry': 165521}, '2019-03-20': {'insu_houseJHeating': 19971, 'insu_house': 3177, 'insu_CNG': 16196, 'insu_bizHeating': 4629, 'insu_salesTwo': 392, 'insu_houseCooking': 1107, 'insu_heatFacility': 37312, 'insu_houseCHeating': 0, 'insu_sum': 203797, 'insu_salesOne': 6745, 'insu_bizCooling': 0, 'insu_heatCombined': 18, 'insu_industry': 114250}, '2019-08-02': {'insu_houseJHeating': 2537, 'insu_house': 282, 'insu_CNG': 16524, 'insu_bizHeating': 290, 'insu_salesTwo': 141, 'insu_houseCooking': 985, 'insu_heatFacility': 17775, 'insu_houseCHeating': 0, 'insu_sum': 141240, 'insu_salesOne': 2765, 'insu_bizCooling': 1808, 'insu_heatCombined': 9544, 'insu_industry': 88589}, '2019-03-02': {'insu_houseJHeating': 21023, 'insu_house': 3715, 'insu_CNG': 15811, 'insu_bizHeating': 3922, 'insu_salesTwo': 361, 'insu_houseCooking': 911, 'insu_heatFacility': 36427, 'insu_houseCHeating': 0, 'insu_sum': 198962, 'insu_salesOne': 5235, 'insu_bizCooling': 0, 'insu_heatCombined': 17, 'insu_industry': 111540}, '2019-01-26': {'insu_houseJHeating': 47644, 'insu_house': 9071, 'insu_CNG': 21673, 'insu_bizHeating': 9624, 'insu_salesTwo': 777, 'insu_houseCooking': 1518, 'insu_heatFacility': 70469, 'insu_houseCHeating': 0, 'insu_sum': 342454, 'insu_salesOne': 9937, 'insu_bizCooling': 0, 'insu_heatCombined': 4, 'insu_industry': 171737}, '2019-05-18': {'insu_houseJHeating': 8143, 'insu_house': 915, 'insu_CNG': 17033, 'insu_bizHeating': 1050, 'insu_salesTwo': 294, 'insu_houseCooking': 1034, 'insu_heatFacility': 19671, 'insu_houseCHeating': 0, 'insu_sum': 179141, 'insu_salesOne': 5207, 'insu_bizCooling': 527, 'insu_heatCombined': 28, 'insu_industry': 125239}, '2019-09-27': {'insu_houseJHeating': 4061, 'insu_house': 711, 'insu_CNG': 19362, 'insu_bizHeating': 420, 'insu_salesTwo': 247, 'insu_houseCooking': 1220, 'insu_heatFacility': 17693, 'insu_houseCHeating': 0, 'insu_sum': 158552, 'insu_salesOne': 2850, 'insu_bizCooling': 843, 'insu_heatCombined': 46, 'insu_industry': 111097}, '2019-09-22': {'insu_houseJHeating': 3264, 'insu_house': 574, 'insu_CNG': 15593, 'insu_bizHeating': 339, 'insu_salesTwo': 199, 'insu_houseCooking': 983, 'insu_heatFacility': 14249, 'insu_houseCHeating': 0, 'insu_sum': 127686, 'insu_salesOne': 2298, 'insu_bizCooling': 680, 'insu_heatCombined': 37, 'insu_industry': 89469}, '2019-01-19': {'insu_houseJHeating': 40684, 'insu_house': 7567, 'insu_CNG': 18476, 'insu_bizHeating': 8273, 'insu_salesTwo': 668, 'insu_houseCooking': 1298, 'insu_heatFacility': 60073, 'insu_houseCHeating': 0, 'insu_sum': 291931, 'insu_salesOne': 8488, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 146400}, '2019-08-12': {'insu_houseJHeating': 1777, 'insu_house': 215, 'insu_CNG': 12111, 'insu_bizHeating': 217, 'insu_salesTwo': 154, 'insu_houseCooking': 685, 'insu_heatFacility': 13027, 'insu_houseCHeating': 0, 'insu_sum': 103515, 'insu_salesOne': 2058, 'insu_bizCooling': 1350, 'insu_heatCombined': 6995, 'insu_industry': 64927}, '2019-05-23': {'insu_houseJHeating': 8016, 'insu_house': 912, 'insu_CNG': 16741, 'insu_bizHeating': 1027, 'insu_salesTwo': 288, 'insu_houseCooking': 1016, 'insu_heatFacility': 19334, 'insu_houseCHeating': 0, 'insu_sum': 176070, 'insu_salesOne': 5100, 'insu_bizCooling': 516, 'insu_heatCombined': 28, 'insu_industry': 123092}, '2019-08-13': {'insu_houseJHeating': 3174, 'insu_house': 385, 'insu_CNG': 21637, 'insu_bizHeating': 387, 'insu_salesTwo': 276, 'insu_houseCooking': 1224, 'insu_heatFacility': 23275, 'insu_houseCHeating': 0, 'insu_sum': 184943, 'insu_salesOne': 3678, 'insu_bizCooling': 2411, 'insu_heatCombined': 12497, 'insu_industry': 116000}, '2019-02-27': {'insu_houseJHeating': 35633, 'insu_house': 5979, 'insu_CNG': 16412, 'insu_bizHeating': 6687, 'insu_salesTwo': 581, 'insu_houseCooking': 1121, 'insu_heatFacility': 55329, 'insu_houseCHeating': 0, 'insu_sum': 245086, 'insu_salesOne': 7703, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 115640}, '2019-09-15': {'insu_houseJHeating': 3400, 'insu_house': 447, 'insu_CNG': 16274, 'insu_bizHeating': 375, 'insu_salesTwo': 215, 'insu_houseCooking': 1026, 'insu_heatFacility': 14871, 'insu_houseCHeating': 0, 'insu_sum': 133260, 'insu_salesOne': 2486, 'insu_bizCooling': 751, 'insu_heatCombined': 39, 'insu_industry': 93375}, '2019-08-06': {'insu_houseJHeating': 2541, 'insu_house': 297, 'insu_CNG': 17251, 'insu_bizHeating': 305, 'insu_salesTwo': 218, 'insu_houseCooking': 1023, 'insu_heatFacility': 18557, 'insu_houseCHeating': 0, 'insu_sum': 147451, 'insu_salesOne': 2910, 'insu_bizCooling': 1902, 'insu_heatCombined': 9964, 'insu_industry': 92484}, '2019-09-20': {'insu_houseJHeating': 5418, 'insu_house': 952, 'insu_CNG': 25905, 'insu_bizHeating': 564, 'insu_salesTwo': 331, 'insu_houseCooking': 1633, 'insu_heatFacility': 23672, 'insu_houseCHeating': 0, 'insu_sum': 212128, 'insu_salesOne': 3823, 'insu_bizCooling': 1131, 'insu_heatCombined': 62, 'insu_industry': 148638}, '2019-09-03': {'insu_houseJHeating': 3067, 'insu_house': 370, 'insu_CNG': 18263, 'insu_bizHeating': 531, 'insu_salesTwo': 306, 'insu_houseCooking': 1013, 'insu_heatFacility': 16688, 'insu_houseCHeating': 0, 'insu_sum': 149545, 'insu_salesOne': 3464, 'insu_bizCooling': 1070, 'insu_heatCombined': 44, 'insu_industry': 104729}, '2019-08-11': {'insu_houseJHeating': 1837, 'insu_house': 222, 'insu_CNG': 12558, 'insu_bizHeating': 225, 'insu_salesTwo': 160, 'insu_houseCooking': 710, 'insu_heatFacility': 13509, 'insu_houseCHeating': 0, 'insu_sum': 107341, 'insu_salesOne': 2138, 'insu_bizCooling': 1401, 'insu_heatCombined': 7253, 'insu_industry': 67326}, '2019-04-23': {'insu_houseJHeating': 14060, 'insu_house': 1948, 'insu_CNG': 19062, 'insu_bizHeating': 2785, 'insu_salesTwo': 355, 'insu_houseCooking': 1168, 'insu_heatFacility': 30118, 'insu_houseCHeating': 0, 'insu_sum': 212794, 'insu_salesOne': 6115, 'insu_bizCooling': 0, 'insu_heatCombined': 43, 'insu_industry': 137139}, '2019-04-05': {'insu_houseJHeating': 12570, 'insu_house': 2174, 'insu_CNG': 16229, 'insu_bizHeating': 2034, 'insu_salesTwo': 261, 'insu_houseCooking': 991, 'insu_heatFacility': 25642, 'insu_houseCHeating': 0, 'insu_sum': 181173, 'insu_salesOne': 4474, 'insu_bizCooling': 0, 'insu_heatCombined': 37, 'insu_industry': 116760}, '2019-02-28': {'insu_houseJHeating': 36722, 'insu_house': 6171, 'insu_CNG': 17171, 'insu_bizHeating': 7226, 'insu_salesTwo': 603, 'insu_houseCooking': 1173, 'insu_heatFacility': 57889, 'insu_houseCHeating': 0, 'insu_sum': 256424, 'insu_salesOne': 8440, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 121028}, '2019-09-07': {'insu_houseJHeating': 3316, 'insu_house': 356, 'insu_CNG': 18268, 'insu_bizHeating': 507, 'insu_salesTwo': 292, 'insu_houseCooking': 1036, 'insu_heatFacility': 16693, 'insu_houseCHeating': 0, 'insu_sum': 149590, 'insu_salesOne': 3299, 'insu_bizCooling': 1020, 'insu_heatCombined': 44, 'insu_industry': 104760}, '2019-08-22': {'insu_houseJHeating': 3884, 'insu_house': 477, 'insu_CNG': 25964, 'insu_bizHeating': 484, 'insu_salesTwo': 350, 'insu_houseCooking': 1471, 'insu_heatFacility': 27929, 'insu_houseCHeating': 0, 'insu_sum': 221924, 'insu_salesOne': 4207, 'insu_bizCooling': 2967, 'insu_heatCombined': 14996, 'insu_industry': 139195}, '2019-06-03': {'insu_houseJHeating': 5867, 'insu_house': 698, 'insu_CNG': 18999, 'insu_bizHeating': 679, 'insu_salesTwo': 193, 'insu_houseCooking': 963, 'insu_heatFacility': 17203, 'insu_houseCHeating': 0, 'insu_sum': 167000, 'insu_salesOne': 3873, 'insu_bizCooling': 1186, 'insu_heatCombined': 17, 'insu_industry': 117321}, '2019-08-09': {'insu_houseJHeating': 2465, 'insu_house': 292, 'insu_CNG': 16817, 'insu_bizHeating': 300, 'insu_salesTwo': 214, 'insu_houseCooking': 953, 'insu_heatFacility': 18090, 'insu_houseCHeating': 0, 'insu_sum': 143739, 'insu_salesOne': 2865, 'insu_bizCooling': 1873, 'insu_heatCombined': 9713, 'insu_industry': 90156}, '2019-05-26': {'insu_houseJHeating': 5985, 'insu_house': 684, 'insu_CNG': 12532, 'insu_bizHeating': 769, 'insu_salesTwo': 216, 'insu_houseCooking': 759, 'insu_heatFacility': 14473, 'insu_houseCHeating': 0, 'insu_sum': 131802, 'insu_salesOne': 3820, 'insu_bizCooling': 399, 'insu_heatCombined': 21, 'insu_industry': 92144}, '2019-06-27': {'insu_houseJHeating': 5168, 'insu_house': 584, 'insu_CNG': 19428, 'insu_bizHeating': 759, 'insu_salesTwo': 222, 'insu_houseCooking': 1274, 'insu_heatFacility': 17592, 'insu_houseCHeating': 0, 'insu_sum': 170772, 'insu_salesOne': 4416, 'insu_bizCooling': 1340, 'insu_heatCombined': 18, 'insu_industry': 119971}, '2019-06-12': {'insu_houseJHeating': 5056, 'insu_house': 657, 'insu_CNG': 17731, 'insu_bizHeating': 642, 'insu_salesTwo': 183, 'insu_houseCooking': 1204, 'insu_heatFacility': 16054, 'insu_houseCHeating': 0, 'insu_sum': 155850, 'insu_salesOne': 3697, 'insu_bizCooling': 1122, 'insu_heatCombined': 16, 'insu_industry': 109488}, '2019-08-03': {'insu_houseJHeating': 3386, 'insu_house': 382, 'insu_CNG': 22444, 'insu_bizHeating': 392, 'insu_salesTwo': 280, 'insu_houseCooking': 1337, 'insu_heatFacility': 24143, 'insu_houseCHeating': 0, 'insu_sum': 191836, 'insu_salesOne': 3742, 'insu_bizCooling': 2446, 'insu_heatCombined': 12963, 'insu_industry': 120323}, '2019-04-03': {'insu_houseJHeating': 11719, 'insu_house': 1944, 'insu_CNG': 14910, 'insu_bizHeating': 1841, 'insu_salesTwo': 237, 'insu_houseCooking': 900, 'insu_heatFacility': 23557, 'insu_houseCHeating': 0, 'insu_sum': 166441, 'insu_salesOne': 4035, 'insu_bizCooling': 0, 'insu_heatCombined': 34, 'insu_industry': 107266}, '2019-04-04': {'insu_houseJHeating': 13781, 'insu_house': 2324, 'insu_CNG': 17611, 'insu_bizHeating': 2175, 'insu_salesTwo': 280, 'insu_houseCooking': 1094, 'insu_heatFacility': 27826, 'insu_houseCHeating': 0, 'insu_sum': 196602, 'insu_salesOne': 4767, 'insu_bizCooling': 0, 'insu_heatCombined': 40, 'insu_industry': 126704}, '2019-02-03': {'insu_houseJHeating': 40197, 'insu_house': 7565, 'insu_CNG': 18614, 'insu_bizHeating': 7664, 'insu_salesTwo': 655, 'insu_houseCooking': 1213, 'insu_heatFacility': 62752, 'insu_houseCHeating': 0, 'insu_sum': 277966, 'insu_salesOne': 8150, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 131154}, '2019-07-16': {'insu_houseJHeating': 3432, 'insu_house': 428, 'insu_CNG': 18347, 'insu_bizHeating': 459, 'insu_salesTwo': 171, 'insu_houseCooking': 1079, 'insu_heatFacility': 20486, 'insu_houseCHeating': 0, 'insu_sum': 151268, 'insu_salesOne': 3588, 'insu_bizCooling': 2004, 'insu_heatCombined': 11, 'insu_industry': 101262}, '2019-05-28': {'insu_houseJHeating': 7931, 'insu_house': 910, 'insu_CNG': 16635, 'insu_bizHeating': 1023, 'insu_salesTwo': 287, 'insu_houseCooking': 1008, 'insu_heatFacility': 19213, 'insu_houseCHeating': 0, 'insu_sum': 174964, 'insu_salesOne': 5081, 'insu_bizCooling': 530, 'insu_heatCombined': 27, 'insu_industry': 122319}, '2019-02-12': {'insu_houseJHeating': 32385, 'insu_house': 5897, 'insu_CNG': 14834, 'insu_bizHeating': 5955, 'insu_salesTwo': 503, 'insu_houseCooking': 1018, 'insu_heatFacility': 50010, 'insu_houseCHeating': 0, 'insu_sum': 221524, 'insu_salesOne': 6399, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 104523}, '2019-01-18': {'insu_houseJHeating': 38119, 'insu_house': 6986, 'insu_CNG': 17343, 'insu_bizHeating': 7780, 'insu_salesTwo': 618, 'insu_houseCooking': 1219, 'insu_heatFacility': 56389, 'insu_houseCHeating': 0, 'insu_sum': 274028, 'insu_salesOne': 8149, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 137422}, '2019-01-21': {'insu_houseJHeating': 34340, 'insu_house': 6385, 'insu_CNG': 15594, 'insu_bizHeating': 6982, 'insu_salesTwo': 564, 'insu_houseCooking': 1094, 'insu_heatFacility': 50702, 'insu_houseCHeating': 0, 'insu_sum': 246390, 'insu_salesOne': 7164, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 123562}, '2019-09-30': {'insu_houseJHeating': 4550, 'insu_house': 802, 'insu_CNG': 18681, 'insu_bizHeating': 715, 'insu_salesTwo': 281, 'insu_houseCooking': 1175, 'insu_heatFacility': 17070, 'insu_houseCHeating': 0, 'insu_sum': 152969, 'insu_salesOne': 3235, 'insu_bizCooling': 586, 'insu_heatCombined': 64, 'insu_industry': 105809}, '2019-01-16': {'insu_houseJHeating': 46035, 'insu_house': 8360, 'insu_CNG': 20923, 'insu_bizHeating': 9402, 'insu_salesTwo': 747, 'insu_houseCooking': 1471, 'insu_heatFacility': 68031, 'insu_houseCHeating': 0, 'insu_sum': 330605, 'insu_salesOne': 9836, 'insu_bizCooling': 0, 'insu_heatCombined': 4, 'insu_industry': 165795}, '2019-03-09': {'insu_houseJHeating': 25589, 'insu_house': 4960, 'insu_CNG': 19917, 'insu_bizHeating': 5092, 'insu_salesTwo': 467, 'insu_houseCooking': 1364, 'insu_heatFacility': 45886, 'insu_houseCHeating': 0, 'insu_sum': 250630, 'insu_salesOne': 6828, 'insu_bizCooling': 0, 'insu_heatCombined': 22, 'insu_industry': 140505}, '2019-07-22': {'insu_houseJHeating': 3005, 'insu_house': 327, 'insu_CNG': 16502, 'insu_bizHeating': 420, 'insu_salesTwo': 146, 'insu_houseCooking': 970, 'insu_heatFacility': 18426, 'insu_houseCHeating': 0, 'insu_sum': 136057, 'insu_salesOne': 3325, 'insu_bizCooling': 1847, 'insu_heatCombined': 10, 'insu_industry': 91079}, '2019-07-05': {'insu_houseJHeating': 5456, 'insu_house': 645, 'insu_CNG': 26007, 'insu_bizHeating': 606, 'insu_salesTwo': 226, 'insu_houseCooking': 1517, 'insu_heatFacility': 29039, 'insu_houseCHeating': 0, 'insu_sum': 214422, 'insu_salesOne': 4728, 'insu_bizCooling': 2644, 'insu_heatCombined': 16, 'insu_industry': 143539}, '2019-01-07': {'insu_houseJHeating': 37973, 'insu_house': 6687, 'insu_CNG': 17137, 'insu_bizHeating': 7696, 'insu_salesTwo': 601, 'insu_houseCooking': 1119, 'insu_heatFacility': 55718, 'insu_houseCHeating': 0, 'insu_sum': 270770, 'insu_salesOne': 8047, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 135788}, '2019-09-21': {'insu_houseJHeating': 3854, 'insu_house': 677, 'insu_CNG': 18415, 'insu_bizHeating': 400, 'insu_salesTwo': 235, 'insu_houseCooking': 1160, 'insu_heatFacility': 16827, 'insu_houseCHeating': 0, 'insu_sum': 150790, 'insu_salesOne': 2716, 'insu_bizCooling': 804, 'insu_heatCombined': 44, 'insu_industry': 105658}, '2019-06-17': {'insu_houseJHeating': 5207, 'insu_house': 586, 'insu_CNG': 19387, 'insu_bizHeating': 750, 'insu_salesTwo': 214, 'insu_houseCooking': 1274, 'insu_heatFacility': 17554, 'insu_houseCHeating': 0, 'insu_sum': 170406, 'insu_salesOne': 4383, 'insu_bizCooling': 1320, 'insu_heatCombined': 18, 'insu_industry': 119714}, '2019-09-28': {'insu_houseJHeating': 4938, 'insu_house': 855, 'insu_CNG': 23538, 'insu_bizHeating': 756, 'insu_salesTwo': 296, 'insu_houseCooking': 1483, 'insu_heatFacility': 21509, 'insu_houseCHeating': 0, 'insu_sum': 192741, 'insu_salesOne': 3458, 'insu_bizCooling': 776, 'insu_heatCombined': 81, 'insu_industry': 135052}, '2019-05-13': {'insu_houseJHeating': 10016, 'insu_house': 1360, 'insu_CNG': 19806, 'insu_bizHeating': 1152, 'insu_salesTwo': 305, 'insu_houseCooking': 1203, 'insu_heatFacility': 22874, 'insu_houseCHeating': 0, 'insu_sum': 208310, 'insu_salesOne': 5369, 'insu_bizCooling': 561, 'insu_heatCombined': 33, 'insu_industry': 145631}, '2019-09-09': {'insu_houseJHeating': 4085, 'insu_house': 405, 'insu_CNG': 21515, 'insu_bizHeating': 577, 'insu_salesTwo': 332, 'insu_houseCooking': 1253, 'insu_heatFacility': 19660, 'insu_houseCHeating': 0, 'insu_sum': 176178, 'insu_salesOne': 3758, 'insu_bizCooling': 1161, 'insu_heatCombined': 52, 'insu_industry': 123380}, '2019-04-20': {'insu_houseJHeating': 17371, 'insu_house': 2414, 'insu_CNG': 23577, 'insu_bizHeating': 3449, 'insu_salesTwo': 440, 'insu_houseCooking': 1445, 'insu_heatFacility': 37251, 'insu_houseCHeating': 0, 'insu_sum': 263194, 'insu_salesOne': 7574, 'insu_bizCooling': 0, 'insu_heatCombined': 53, 'insu_industry': 169620}, '2019-02-15': {'insu_houseJHeating': 37165, 'insu_house': 6599, 'insu_CNG': 17149, 'insu_bizHeating': 7050, 'insu_salesTwo': 597, 'insu_houseCooking': 1176, 'insu_heatFacility': 57813, 'insu_houseCHeating': 0, 'insu_sum': 256089, 'insu_salesOne': 7708, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 120832}, '2019-06-18': {'insu_houseJHeating': 4749, 'insu_house': 539, 'insu_CNG': 17654, 'insu_bizHeating': 683, 'insu_salesTwo': 195, 'insu_houseCooking': 1161, 'insu_heatFacility': 15985, 'insu_houseCHeating': 0, 'insu_sum': 155180, 'insu_salesOne': 3974, 'insu_bizCooling': 1205, 'insu_heatCombined': 16, 'insu_industry': 109017}, '2019-06-16': {'insu_houseJHeating': 4172, 'insu_house': 470, 'insu_CNG': 15542, 'insu_bizHeating': 601, 'insu_salesTwo': 172, 'insu_houseCooking': 1022, 'insu_heatFacility': 14072, 'insu_houseCHeating': 0, 'insu_sum': 136609, 'insu_salesOne': 3515, 'insu_bizCooling': 1059, 'insu_heatCombined': 14, 'insu_industry': 95971}, '2019-09-05': {'insu_houseJHeating': 3282, 'insu_house': 378, 'insu_CNG': 18885, 'insu_bizHeating': 539, 'insu_salesTwo': 310, 'insu_houseCooking': 1050, 'insu_heatFacility': 17257, 'insu_houseCHeating': 0, 'insu_sum': 154642, 'insu_salesOne': 3513, 'insu_bizCooling': 1085, 'insu_heatCombined': 45, 'insu_industry': 108298}, '2019-09-18': {'insu_houseJHeating': 4148, 'insu_house': 728, 'insu_CNG': 19842, 'insu_bizHeating': 432, 'insu_salesTwo': 254, 'insu_houseCooking': 1252, 'insu_heatFacility': 18132, 'insu_houseCHeating': 0, 'insu_sum': 162480, 'insu_salesOne': 2928, 'insu_bizCooling': 867, 'insu_heatCombined': 48, 'insu_industry': 113849}, '2019-07-14': {'insu_houseJHeating': 3225, 'insu_house': 384, 'insu_CNG': 16511, 'insu_bizHeating': 403, 'insu_salesTwo': 151, 'insu_houseCooking': 978, 'insu_heatFacility': 18436, 'insu_houseCHeating': 0, 'insu_sum': 136128, 'insu_salesOne': 3142, 'insu_bizCooling': 1760, 'insu_heatCombined': 10, 'insu_industry': 91127}, '2019-02-21': {'insu_houseJHeating': 41233, 'insu_house': 6991, 'insu_CNG': 19060, 'insu_bizHeating': 7851, 'insu_salesTwo': 684, 'insu_houseCooking': 1307, 'insu_heatFacility': 64256, 'insu_houseCHeating': 0, 'insu_sum': 284629, 'insu_salesOne': 8949, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 134298}, '2019-01-29': {'insu_houseJHeating': 32065, 'insu_house': 6122, 'insu_CNG': 14583, 'insu_bizHeating': 6465, 'insu_salesTwo': 522, 'insu_houseCooking': 1021, 'insu_heatFacility': 47417, 'insu_houseCHeating': 0, 'insu_sum': 230428, 'insu_salesOne': 6674, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 115557}, '2019-08-23': {'insu_houseJHeating': 2939, 'insu_house': 363, 'insu_CNG': 19649, 'insu_bizHeating': 366, 'insu_salesTwo': 265, 'insu_houseCooking': 1113, 'insu_heatFacility': 21136, 'insu_houseCHeating': 0, 'insu_sum': 167947, 'insu_salesOne': 3183, 'insu_bizCooling': 2245, 'insu_heatCombined': 11349, 'insu_industry': 105340}, '2019-09-26': {'insu_houseJHeating': 3143, 'insu_house': 552, 'insu_CNG': 15001, 'insu_bizHeating': 326, 'insu_salesTwo': 192, 'insu_houseCooking': 945, 'insu_heatFacility': 13708, 'insu_houseCHeating': 0, 'insu_sum': 122837, 'insu_salesOne': 2210, 'insu_bizCooling': 654, 'insu_heatCombined': 36, 'insu_industry': 86072}, '2019-01-06': {'insu_houseJHeating': 31735, 'insu_house': 5609, 'insu_CNG': 14342, 'insu_bizHeating': 6456, 'insu_salesTwo': 504, 'insu_houseCooking': 937, 'insu_heatFacility': 46632, 'insu_houseCHeating': 0, 'insu_sum': 226615, 'insu_salesOne': 6751, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 113645}, '2019-07-07': {'insu_houseJHeating': 2959, 'insu_house': 368, 'insu_CNG': 14545, 'insu_bizHeating': 346, 'insu_salesTwo': 129, 'insu_houseCooking': 839, 'insu_heatFacility': 16241, 'insu_houseCHeating': 0, 'insu_sum': 119923, 'insu_salesOne': 2699, 'insu_bizCooling': 1509, 'insu_heatCombined': 9, 'insu_industry': 80279}, '2019-05-08': {'insu_houseJHeating': 8354, 'insu_house': 1317, 'insu_CNG': 15993, 'insu_bizHeating': 873, 'insu_salesTwo': 230, 'insu_houseCooking': 926, 'insu_heatFacility': 18470, 'insu_houseCHeating': 0, 'insu_sum': 168204, 'insu_salesOne': 4000, 'insu_bizCooling': 423, 'insu_heatCombined': 26, 'insu_industry': 117593}, '2019-06-23': {'insu_houseJHeating': 4119, 'insu_house': 461, 'insu_CNG': 15400, 'insu_bizHeating': 600, 'insu_salesTwo': 175, 'insu_houseCooking': 1011, 'insu_heatFacility': 13944, 'insu_houseCHeating': 0, 'insu_sum': 135367, 'insu_salesOne': 3486, 'insu_bizCooling': 1058, 'insu_heatCombined': 14, 'insu_industry': 95098}, '2019-02-16': {'insu_houseJHeating': 28411, 'insu_house': 5029, 'insu_CNG': 13115, 'insu_bizHeating': 5396, 'insu_salesTwo': 457, 'insu_houseCooking': 899, 'insu_heatFacility': 44214, 'insu_houseCHeating': 0, 'insu_sum': 195849, 'insu_salesOne': 5919, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 92409}, '2019-06-05': {'insu_houseJHeating': 5795, 'insu_house': 692, 'insu_CNG': 18824, 'insu_bizHeating': 674, 'insu_salesTwo': 192, 'insu_houseCooking': 955, 'insu_heatFacility': 17045, 'insu_houseCHeating': 0, 'insu_sum': 165463, 'insu_salesOne': 3849, 'insu_bizCooling': 1178, 'insu_heatCombined': 17, 'insu_industry': 116241}, '2019-02-05': {'insu_houseJHeating': 35152, 'insu_house': 6613, 'insu_CNG': 16252, 'insu_bizHeating': 6661, 'insu_salesTwo': 570, 'insu_houseCooking': 1060, 'insu_heatFacility': 54789, 'insu_houseCHeating': 0, 'insu_sum': 242695, 'insu_salesOne': 7086, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 114512}, '2019-08-17': {'insu_houseJHeating': 3347, 'insu_house': 404, 'insu_CNG': 22880, 'insu_bizHeating': 415, 'insu_salesTwo': 296, 'insu_houseCooking': 1299, 'insu_heatFacility': 24612, 'insu_houseCHeating': 0, 'insu_sum': 195565, 'insu_salesOne': 3852, 'insu_bizCooling': 2584, 'insu_heatCombined': 13215, 'insu_industry': 122662}, '2019-10-02': {'insu_houseJHeating': 9506, 'insu_house': 1642, 'insu_CNG': 15937, 'insu_bizHeating': 2371, 'insu_salesTwo': 570, 'insu_houseCooking': 1253, 'insu_heatFacility': 19513, 'insu_houseCHeating': 0, 'insu_sum': 167357, 'insu_salesOne': 6626, 'insu_bizCooling': 0, 'insu_heatCombined': 49, 'insu_industry': 109891}, '2019-05-22': {'insu_houseJHeating': 7558, 'insu_house': 850, 'insu_CNG': 15794, 'insu_bizHeating': 972, 'insu_salesTwo': 273, 'insu_houseCooking': 958, 'insu_heatFacility': 18241, 'insu_houseCHeating': 0, 'insu_sum': 166118, 'insu_salesOne': 4823, 'insu_bizCooling': 488, 'insu_heatCombined': 26, 'insu_industry': 116135}, '2019-04-06': {'insu_houseJHeating': 15720, 'insu_house': 2790, 'insu_CNG': 20488, 'insu_bizHeating': 2604, 'insu_salesTwo': 335, 'insu_houseCooking': 1251, 'insu_heatFacility': 32371, 'insu_houseCHeating': 0, 'insu_sum': 228711, 'insu_salesOne': 5710, 'insu_bizCooling': 0, 'insu_heatCombined': 46, 'insu_industry': 147397}, '2019-01-10': {'insu_houseJHeating': 40293, 'insu_house': 7218, 'insu_CNG': 18322, 'insu_bizHeating': 8289, 'insu_salesTwo': 647, 'insu_houseCooking': 1289, 'insu_heatFacility': 59574, 'insu_houseCHeating': 0, 'insu_sum': 289508, 'insu_salesOne': 8686, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 145185}, '2019-03-13': {'insu_houseJHeating': 25042, 'insu_house': 4465, 'insu_CNG': 19726, 'insu_bizHeating': 5297, 'insu_salesTwo': 433, 'insu_houseCooking': 1351, 'insu_heatFacility': 45446, 'insu_houseCHeating': 0, 'insu_sum': 248228, 'insu_salesOne': 7288, 'insu_bizCooling': 0, 'insu_heatCombined': 21, 'insu_industry': 139159}, '2019-03-10': {'insu_houseJHeating': 22315, 'insu_house': 4438, 'insu_CNG': 17562, 'insu_bizHeating': 4564, 'insu_salesTwo': 419, 'insu_houseCooking': 1203, 'insu_heatFacility': 40459, 'insu_houseCHeating': 0, 'insu_sum': 220989, 'insu_salesOne': 6121, 'insu_bizCooling': 0, 'insu_heatCombined': 19, 'insu_industry': 123888}, '2019-05-24': {'insu_houseJHeating': 9557, 'insu_house': 1092, 'insu_CNG': 19980, 'insu_bizHeating': 1227, 'insu_salesTwo': 344, 'insu_houseCooking': 1212, 'insu_heatFacility': 23075, 'insu_houseCHeating': 0, 'insu_sum': 210141, 'insu_salesOne': 6092, 'insu_bizCooling': 617, 'insu_heatCombined': 33, 'insu_industry': 146911}, '2019-08-07': {'insu_houseJHeating': 2495, 'insu_house': 296, 'insu_CNG': 17106, 'insu_bizHeating': 304, 'insu_salesTwo': 217, 'insu_houseCooking': 1012, 'insu_heatFacility': 18401, 'insu_houseCHeating': 0, 'insu_sum': 146210, 'insu_salesOne': 2899, 'insu_bizCooling': 1895, 'insu_heatCombined': 9880, 'insu_industry': 91706}, '2019-05-12': {'insu_houseJHeating': 7402, 'insu_house': 1021, 'insu_CNG': 14568, 'insu_bizHeating': 838, 'insu_salesTwo': 222, 'insu_houseCooking': 885, 'insu_heatFacility': 16825, 'insu_houseCHeating': 0, 'insu_sum': 153220, 'insu_salesOne': 3909, 'insu_bizCooling': 408, 'insu_heatCombined': 24, 'insu_industry': 107117}, '2019-08-31': {'insu_houseJHeating': 3769, 'insu_house': 468, 'insu_CNG': 24075, 'insu_bizHeating': 580, 'insu_salesTwo': 388, 'insu_houseCooking': 1360, 'insu_heatFacility': 25898, 'insu_houseCHeating': 0, 'insu_sum': 205784, 'insu_salesOne': 4372, 'insu_bizCooling': 1871, 'insu_heatCombined': 13926, 'insu_industry': 129076}, '2019-06-19': {'insu_houseJHeating': 4927, 'insu_house': 549, 'insu_CNG': 18366, 'insu_bizHeating': 715, 'insu_salesTwo': 209, 'insu_houseCooking': 1207, 'insu_heatFacility': 16630, 'insu_houseCHeating': 0, 'insu_sum': 161436, 'insu_salesOne': 4141, 'insu_bizCooling': 1263, 'insu_heatCombined': 17, 'insu_industry': 113412}, '2019-07-27': {'insu_houseJHeating': 4075, 'insu_house': 443, 'insu_CNG': 22403, 'insu_bizHeating': 566, 'insu_salesTwo': 196, 'insu_houseCooking': 1308, 'insu_heatFacility': 25014, 'insu_houseCHeating': 0, 'insu_sum': 184703, 'insu_salesOne': 4555, 'insu_bizCooling': 2485, 'insu_heatCombined': 14, 'insu_industry': 123644}, '2019-04-27': {'insu_houseJHeating': 12866, 'insu_house': 1792, 'insu_CNG': 17230, 'insu_bizHeating': 2345, 'insu_salesTwo': 324, 'insu_houseCooking': 1057, 'insu_heatFacility': 27224, 'insu_houseCHeating': 0, 'insu_sum': 192345, 'insu_salesOne': 5518, 'insu_bizCooling': 0, 'insu_heatCombined': 30, 'insu_industry': 123960}, '2019-03-21': {'insu_houseJHeating': 25734, 'insu_house': 4099, 'insu_CNG': 20871, 'insu_bizHeating': 5965, 'insu_salesTwo': 505, 'insu_houseCooking': 1427, 'insu_heatFacility': 48084, 'insu_houseCHeating': 0, 'insu_sum': 262633, 'insu_salesOne': 8691, 'insu_bizCooling': 0, 'insu_heatCombined': 23, 'insu_industry': 147234}, '2019-05-05': {'insu_houseJHeating': 9068, 'insu_house': 1419, 'insu_CNG': 17301, 'insu_bizHeating': 943, 'insu_salesTwo': 248, 'insu_houseCooking': 1001, 'insu_heatFacility': 19981, 'insu_houseCHeating': 0, 'insu_sum': 181965, 'insu_salesOne': 4304, 'insu_bizCooling': 457, 'insu_heatCombined': 28, 'insu_industry': 127213}, '2019-04-02': {'insu_houseJHeating': 10915, 'insu_house': 1807, 'insu_CNG': 13880, 'insu_bizHeating': 1711, 'insu_salesTwo': 220, 'insu_houseCooking': 842, 'insu_heatFacility': 21930, 'insu_houseCHeating': 0, 'insu_sum': 154944, 'insu_salesOne': 3751, 'insu_bizCooling': 0, 'insu_heatCombined': 31, 'insu_industry': 99856}, '2019-03-06': {'insu_houseJHeating': 26620, 'insu_house': 5081, 'insu_CNG': 20517, 'insu_bizHeating': 5262, 'insu_salesTwo': 483, 'insu_houseCooking': 1162, 'insu_heatFacility': 47267, 'insu_houseCHeating': 0, 'insu_sum': 258173, 'insu_salesOne': 7025, 'insu_bizCooling': 0, 'insu_heatCombined': 22, 'insu_industry': 144734}, '2019-01-27': {'insu_houseJHeating': 37294, 'insu_house': 7099, 'insu_CNG': 16964, 'insu_bizHeating': 7532, 'insu_salesTwo': 608, 'insu_houseCooking': 1188, 'insu_heatFacility': 55156, 'insu_houseCHeating': 0, 'insu_sum': 268039, 'insu_salesOne': 7777, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 134419}, '2019-08-08': {'insu_houseJHeating': 3307, 'insu_house': 392, 'insu_CNG': 22642, 'insu_bizHeating': 402, 'insu_salesTwo': 288, 'insu_houseCooking': 1327, 'insu_heatFacility': 24356, 'insu_houseCHeating': 0, 'insu_sum': 193529, 'insu_salesOne': 3841, 'insu_bizCooling': 2512, 'insu_heatCombined': 13077, 'insu_industry': 121385}, '2019-09-13': {'insu_houseJHeating': 5376, 'insu_house': 535, 'insu_CNG': 25358, 'insu_bizHeating': 601, 'insu_salesTwo': 345, 'insu_houseCooking': 1597, 'insu_heatFacility': 23172, 'insu_houseCHeating': 0, 'insu_sum': 207650, 'insu_salesOne': 3975, 'insu_bizCooling': 1208, 'insu_heatCombined': 61, 'insu_industry': 145421}, '2019-05-20': {'insu_houseJHeating': 8378, 'insu_house': 941, 'insu_CNG': 17507, 'insu_bizHeating': 1078, 'insu_salesTwo': 302, 'insu_houseCooking': 1062, 'insu_heatFacility': 20219, 'insu_houseCHeating': 0, 'insu_sum': 184126, 'insu_salesOne': 5345, 'insu_bizCooling': 541, 'insu_heatCombined': 29, 'insu_industry': 128724}, '2019-05-11': {'insu_houseJHeating': 8472, 'insu_house': 1240, 'insu_CNG': 16593, 'insu_bizHeating': 939, 'insu_salesTwo': 248, 'insu_houseCooking': 1010, 'insu_heatFacility': 19163, 'insu_houseCHeating': 0, 'insu_sum': 174515, 'insu_salesOne': 4361, 'insu_bizCooling': 457, 'insu_heatCombined': 27, 'insu_industry': 122005}, '2019-05-27': {'insu_houseJHeating': 8533, 'insu_house': 976, 'insu_CNG': 17867, 'insu_bizHeating': 1097, 'insu_salesTwo': 308, 'insu_houseCooking': 1082, 'insu_heatFacility': 20635, 'insu_houseCHeating': 0, 'insu_sum': 187916, 'insu_salesOne': 5448, 'insu_bizCooling': 568, 'insu_heatCombined': 29, 'insu_industry': 131374}, '2019-01-24': {'insu_houseJHeating': 42594, 'insu_house': 8097, 'insu_CNG': 19381, 'insu_bizHeating': 8642, 'insu_salesTwo': 698, 'insu_houseCooking': 1358, 'insu_heatFacility': 63016, 'insu_houseCHeating': 0, 'insu_sum': 306235, 'insu_salesOne': 8872, 'insu_bizCooling': 0, 'insu_heatCombined': 4, 'insu_industry': 153574}, '2019-02-02': {'insu_houseJHeating': 43115, 'insu_house': 8209, 'insu_CNG': 20075, 'insu_bizHeating': 8343, 'insu_salesTwo': 714, 'insu_houseCooking': 1328, 'insu_heatFacility': 67677, 'insu_houseCHeating': 0, 'insu_sum': 299783, 'insu_salesOne': 8873, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 141448}, '2019-01-22': {'insu_houseJHeating': 30033, 'insu_house': 5666, 'insu_CNG': 13656, 'insu_bizHeating': 6099, 'insu_salesTwo': 492, 'insu_houseCooking': 957, 'insu_heatFacility': 44403, 'insu_houseCHeating': 0, 'insu_sum': 215780, 'insu_salesOne': 6259, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 108211}, '2019-07-20': {'insu_houseJHeating': 4219, 'insu_house': 459, 'insu_CNG': 23156, 'insu_bizHeating': 589, 'insu_salesTwo': 204, 'insu_houseCooking': 1362, 'insu_heatFacility': 25855, 'insu_houseCHeating': 0, 'insu_sum': 190912, 'insu_salesOne': 4663, 'insu_bizCooling': 2590, 'insu_heatCombined': 14, 'insu_industry': 127800}, '2019-07-18': {'insu_houseJHeating': 4306, 'insu_house': 521, 'insu_CNG': 23719, 'insu_bizHeating': 601, 'insu_salesTwo': 225, 'insu_houseCooking': 1395, 'insu_heatFacility': 26485, 'insu_houseCHeating': 0, 'insu_sum': 195559, 'insu_salesOne': 4753, 'insu_bizCooling': 2629, 'insu_heatCombined': 14, 'insu_industry': 130911}, '2019-02-19': {'insu_houseJHeating': 28185, 'insu_house': 4782, 'insu_CNG': 13046, 'insu_bizHeating': 5393, 'insu_salesTwo': 470, 'insu_houseCooking': 895, 'insu_heatFacility': 43981, 'insu_houseCHeating': 0, 'insu_sum': 194818, 'insu_salesOne': 6144, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 91922}, '2019-07-31': {'insu_houseJHeating': 3183, 'insu_house': 347, 'insu_CNG': 17313, 'insu_bizHeating': 369, 'insu_salesTwo': 155, 'insu_houseCooking': 1009, 'insu_heatFacility': 19332, 'insu_houseCHeating': 0, 'insu_sum': 142743, 'insu_salesOne': 3438, 'insu_bizCooling': 2040, 'insu_heatCombined': 6, 'insu_industry': 95552}, '2019-09-08': {'insu_houseJHeating': 2734, 'insu_house': 285, 'insu_CNG': 14782, 'insu_bizHeating': 405, 'insu_salesTwo': 233, 'insu_houseCooking': 840, 'insu_heatFacility': 13508, 'insu_houseCHeating': 0, 'insu_sum': 121045, 'insu_salesOne': 2638, 'insu_bizCooling': 815, 'insu_heatCombined': 35, 'insu_industry': 84770}, '2019-05-15': {'insu_houseJHeating': 8162, 'insu_house': 1112, 'insu_CNG': 17005, 'insu_bizHeating': 1039, 'insu_salesTwo': 281, 'insu_houseCooking': 1033, 'insu_heatFacility': 19639, 'insu_houseCHeating': 0, 'insu_sum': 178850, 'insu_salesOne': 4997, 'insu_bizCooling': 517, 'insu_heatCombined': 28, 'insu_industry': 125036}, '2019-07-23': {'insu_houseJHeating': 3029, 'insu_house': 327, 'insu_CNG': 16564, 'insu_bizHeating': 421, 'insu_salesTwo': 146, 'insu_houseCooking': 973, 'insu_heatFacility': 18495, 'insu_houseCHeating': 0, 'insu_sum': 136563, 'insu_salesOne': 3333, 'insu_bizCooling': 1847, 'insu_heatCombined': 10, 'insu_industry': 91418}, '2019-08-25': {'insu_houseJHeating': 2501, 'insu_house': 310, 'insu_CNG': 16779, 'insu_bizHeating': 311, 'insu_salesTwo': 225, 'insu_houseCooking': 950, 'insu_heatFacility': 18050, 'insu_houseCHeating': 0, 'insu_sum': 143421, 'insu_salesOne': 2738, 'insu_bizCooling': 1909, 'insu_heatCombined': 9691, 'insu_industry': 89956}, '2019-06-26': {'insu_houseJHeating': 5202, 'insu_house': 583, 'insu_CNG': 19455, 'insu_bizHeating': 758, 'insu_salesTwo': 221, 'insu_houseCooking': 1275, 'insu_heatFacility': 17615, 'insu_houseCHeating': 0, 'insu_sum': 171004, 'insu_salesOne': 4406, 'insu_bizCooling': 1337, 'insu_heatCombined': 18, 'insu_industry': 120134}, '2019-07-28': {'insu_houseJHeating': 2212, 'insu_house': 243, 'insu_CNG': 12114, 'insu_bizHeating': 280, 'insu_salesTwo': 108, 'insu_houseCooking': 707, 'insu_heatFacility': 13526, 'insu_houseCHeating': 0, 'insu_sum': 99876, 'insu_salesOne': 2406, 'insu_bizCooling': 1418, 'insu_heatCombined': 4, 'insu_industry': 66857}, '2019-06-10': {'insu_houseJHeating': 5748, 'insu_house': 749, 'insu_CNG': 19582, 'insu_bizHeating': 703, 'insu_salesTwo': 200, 'insu_houseCooking': 1206, 'insu_heatFacility': 17730, 'insu_houseCHeating': 0, 'insu_sum': 172119, 'insu_salesOne': 4039, 'insu_bizCooling': 1228, 'insu_heatCombined': 18, 'insu_industry': 120917}, '2019-03-11': {'insu_houseJHeating': 22745, 'insu_house': 4630, 'insu_CNG': 18073, 'insu_bizHeating': 4762, 'insu_salesTwo': 437, 'insu_houseCooking': 1238, 'insu_heatFacility': 41637, 'insu_houseCHeating': 0, 'insu_sum': 227418, 'insu_salesOne': 6386, 'insu_bizCooling': 0, 'insu_heatCombined': 20, 'insu_industry': 127492}, '2019-05-19': {'insu_houseJHeating': 6883, 'insu_house': 773, 'insu_CNG': 14384, 'insu_bizHeating': 885, 'insu_salesTwo': 248, 'insu_houseCooking': 873, 'insu_heatFacility': 16612, 'insu_houseCHeating': 0, 'insu_sum': 151284, 'insu_salesOne': 4392, 'insu_bizCooling': 445, 'insu_heatCombined': 24, 'insu_industry': 105764}, '2019-05-29': {'insu_houseJHeating': 7919, 'insu_house': 909, 'insu_CNG': 16608, 'insu_bizHeating': 1022, 'insu_salesTwo': 287, 'insu_houseCooking': 1006, 'insu_heatFacility': 19181, 'insu_houseCHeating': 0, 'insu_sum': 174675, 'insu_salesOne': 5070, 'insu_bizCooling': 529, 'insu_heatCombined': 27, 'insu_industry': 122117}, '2019-04-09': {'insu_houseJHeating': 13493, 'insu_house': 2415, 'insu_CNG': 17646, 'insu_bizHeating': 2252, 'insu_salesTwo': 289, 'insu_houseCooking': 1081, 'insu_heatFacility': 27881, 'insu_houseCHeating': 0, 'insu_sum': 196991, 'insu_salesOne': 4938, 'insu_bizCooling': 0, 'insu_heatCombined': 40, 'insu_industry': 126954}, '2019-03-16': {'insu_houseJHeating': 22363, 'insu_house': 4078, 'insu_CNG': 18179, 'insu_bizHeating': 5160, 'insu_salesTwo': 422, 'insu_houseCooking': 1245, 'insu_heatFacility': 41881, 'insu_houseCHeating': 0, 'insu_sum': 228752, 'insu_salesOne': 7164, 'insu_bizCooling': 0, 'insu_heatCombined': 20, 'insu_industry': 128240}, '2019-03-23': {'insu_houseJHeating': 25031, 'insu_house': 3985, 'insu_CNG': 20283, 'insu_bizHeating': 5787, 'insu_salesTwo': 490, 'insu_houseCooking': 1388, 'insu_heatFacility': 46728, 'insu_houseCHeating': 0, 'insu_sum': 255230, 'insu_salesOne': 8432, 'insu_bizCooling': 0, 'insu_heatCombined': 22, 'insu_industry': 143084}, '2019-07-02': {'insu_houseJHeating': 3869, 'insu_house': 447, 'insu_CNG': 18199, 'insu_bizHeating': 422, 'insu_salesTwo': 158, 'insu_houseCooking': 1075, 'insu_heatFacility': 20321, 'insu_houseCHeating': 0, 'insu_sum': 150045, 'insu_salesOne': 3261, 'insu_bizCooling': 1842, 'insu_heatCombined': 9, 'insu_industry': 100443}, '2019-08-01': {'insu_houseJHeating': 3470, 'insu_house': 385, 'insu_CNG': 22604, 'insu_bizHeating': 396, 'insu_salesTwo': 193, 'insu_houseCooking': 1358, 'insu_heatFacility': 24316, 'insu_houseCHeating': 0, 'insu_sum': 193209, 'insu_salesOne': 3778, 'insu_bizCooling': 2469, 'insu_heatCombined': 13056, 'insu_industry': 121185}, '2019-08-05': {'insu_houseJHeating': 2441, 'insu_house': 282, 'insu_CNG': 16462, 'insu_bizHeating': 290, 'insu_salesTwo': 207, 'insu_houseCooking': 978, 'insu_heatFacility': 17708, 'insu_houseCHeating': 0, 'insu_sum': 140708, 'insu_salesOne': 2768, 'insu_bizCooling': 1809, 'insu_heatCombined': 9508, 'insu_industry': 88255}, '2019-01-20': {'insu_houseJHeating': 33777, 'insu_house': 6281, 'insu_CNG': 15337, 'insu_bizHeating': 6867, 'insu_salesTwo': 554, 'insu_houseCooking': 1077, 'insu_heatFacility': 49869, 'insu_houseCHeating': 0, 'insu_sum': 242344, 'insu_salesOne': 7046, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 121533}, '2019-01-04': {'insu_houseJHeating': 41152, 'insu_house': 7131, 'insu_CNG': 18523, 'insu_bizHeating': 8323, 'insu_salesTwo': 650, 'insu_houseCooking': 1194, 'insu_heatFacility': 60227, 'insu_houseCHeating': 0, 'insu_sum': 292681, 'insu_salesOne': 8701, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 146776}, '2019-06-04': {'insu_houseJHeating': 5676, 'insu_house': 676, 'insu_CNG': 18440, 'insu_bizHeating': 657, 'insu_salesTwo': 187, 'insu_houseCooking': 943, 'insu_heatFacility': 16697, 'insu_houseCHeating': 0, 'insu_sum': 162088, 'insu_salesOne': 3776, 'insu_bizCooling': 1148, 'insu_heatCombined': 17, 'insu_industry': 113870}, '2019-04-26': {'insu_houseJHeating': 13802, 'insu_house': 1918, 'insu_CNG': 18709, 'insu_bizHeating': 2723, 'insu_salesTwo': 347, 'insu_houseCooking': 1147, 'insu_heatFacility': 29561, 'insu_houseCHeating': 0, 'insu_sum': 208856, 'insu_salesOne': 6006, 'insu_bizCooling': 0, 'insu_heatCombined': 42, 'insu_industry': 134601}, '2019-04-01': {'insu_houseJHeating': 12267, 'insu_house': 2023, 'insu_CNG': 15596, 'insu_bizHeating': 1925, 'insu_salesTwo': 247, 'insu_houseCooking': 947, 'insu_heatFacility': 24642, 'insu_houseCHeating': 0, 'insu_sum': 174105, 'insu_salesOne': 4218, 'insu_bizCooling': 0, 'insu_heatCombined': 35, 'insu_industry': 112205}, '2019-03-01': {'insu_houseJHeating': 27872, 'insu_house': 4904, 'insu_CNG': 20967, 'insu_bizHeating': 5215, 'insu_salesTwo': 480, 'insu_houseCooking': 1207, 'insu_heatFacility': 48305, 'insu_houseCHeating': 0, 'insu_sum': 263840, 'insu_salesOne': 6957, 'insu_bizCooling': 0, 'insu_heatCombined': 23, 'insu_industry': 147911}, '2019-04-12': {'insu_houseJHeating': 15065, 'insu_house': 2431, 'insu_CNG': 19616, 'insu_bizHeating': 2560, 'insu_salesTwo': 329, 'insu_houseCooking': 1203, 'insu_heatFacility': 30994, 'insu_houseCHeating': 0, 'insu_sum': 218985, 'insu_salesOne': 5614, 'insu_bizCooling': 0, 'insu_heatCombined': 44, 'insu_industry': 141129}, '2019-03-29': {'insu_houseJHeating': 22912, 'insu_house': 3661, 'insu_CNG': 18249, 'insu_bizHeating': 4696, 'insu_salesTwo': 445, 'insu_houseCooking': 1249, 'insu_heatFacility': 42044, 'insu_houseCHeating': 0, 'insu_sum': 229641, 'insu_salesOne': 7459, 'insu_bizCooling': 0, 'insu_heatCombined': 46, 'insu_industry': 128880}, '2019-06-09': {'insu_houseJHeating': 4247, 'insu_house': 544, 'insu_CNG': 14339, 'insu_bizHeating': 511, 'insu_salesTwo': 145, 'insu_houseCooking': 883, 'insu_heatFacility': 12984, 'insu_houseCHeating': 0, 'insu_sum': 126041, 'insu_salesOne': 2936, 'insu_bizCooling': 892, 'insu_heatCombined': 13, 'insu_industry': 88546}, '2019-02-17': {'insu_houseJHeating': 31777, 'insu_house': 5627, 'insu_CNG': 14674, 'insu_bizHeating': 6042, 'insu_salesTwo': 512, 'insu_houseCooking': 1006, 'insu_heatFacility': 49469, 'insu_houseCHeating': 0, 'insu_sum': 219127, 'insu_salesOne': 6628, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 103392}, '2019-07-26': {'insu_houseJHeating': 3028, 'insu_house': 329, 'insu_CNG': 16644, 'insu_bizHeating': 421, 'insu_salesTwo': 146, 'insu_houseCooking': 976, 'insu_heatFacility': 18584, 'insu_houseCHeating': 0, 'insu_sum': 137224, 'insu_salesOne': 3380, 'insu_bizCooling': 1846, 'insu_heatCombined': 10, 'insu_industry': 91861}, '2019-01-14': {'insu_houseJHeating': 37824, 'insu_house': 6814, 'insu_CNG': 17181, 'insu_bizHeating': 7728, 'insu_salesTwo': 603, 'insu_houseCooking': 1208, 'insu_heatFacility': 55864, 'insu_houseCHeating': 0, 'insu_sum': 271476, 'insu_salesOne': 8108, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 136142}, '2019-08-27': {'insu_houseJHeating': 2731, 'insu_house': 338, 'insu_CNG': 18316, 'insu_bizHeating': 340, 'insu_salesTwo': 246, 'insu_houseCooking': 1036, 'insu_heatFacility': 19703, 'insu_houseCHeating': 0, 'insu_sum': 156557, 'insu_salesOne': 2989, 'insu_bizCooling': 2084, 'insu_heatCombined': 10579, 'insu_industry': 98196}, '2019-01-28': {'insu_houseJHeating': 41103, 'insu_house': 7821, 'insu_CNG': 18693, 'insu_bizHeating': 8298, 'insu_salesTwo': 670, 'insu_houseCooking': 1308, 'insu_heatFacility': 60779, 'insu_houseCHeating': 0, 'insu_sum': 295364, 'insu_salesOne': 8566, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 148122}, '2019-02-09': {'insu_houseJHeating': 40680, 'insu_house': 7558, 'insu_CNG': 18727, 'insu_bizHeating': 7576, 'insu_salesTwo': 648, 'insu_houseCooking': 1287, 'insu_heatFacility': 63132, 'insu_houseCHeating': 0, 'insu_sum': 279650, 'insu_salesOne': 8093, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 131949}, '2019-09-12': {'insu_houseJHeating': 3692, 'insu_house': 352, 'insu_CNG': 18795, 'insu_bizHeating': 483, 'insu_salesTwo': 278, 'insu_houseCooking': 1184, 'insu_heatFacility': 17175, 'insu_houseCHeating': 0, 'insu_sum': 153909, 'insu_salesOne': 3147, 'insu_bizCooling': 972, 'insu_heatCombined': 45, 'insu_industry': 107785}, '2019-09-17': {'insu_houseJHeating': 3855, 'insu_house': 508, 'insu_CNG': 18335, 'insu_bizHeating': 419, 'insu_salesTwo': 240, 'insu_houseCooking': 1156, 'insu_heatFacility': 16754, 'insu_houseCHeating': 0, 'insu_sum': 150137, 'insu_salesOne': 2785, 'insu_bizCooling': 840, 'insu_heatCombined': 44, 'insu_industry': 105201}, '2019-01-23': {'insu_houseJHeating': 42533, 'insu_house': 8070, 'insu_CNG': 19354, 'insu_bizHeating': 8637, 'insu_salesTwo': 697, 'insu_houseCooking': 1356, 'insu_heatFacility': 62927, 'insu_houseCHeating': 0, 'insu_sum': 305800, 'insu_salesOne': 8867, 'insu_bizCooling': 0, 'insu_heatCombined': 4, 'insu_industry': 153356}, '2019-03-19': {'insu_houseJHeating': 18987, 'insu_house': 3014, 'insu_CNG': 15401, 'insu_bizHeating': 4407, 'insu_salesTwo': 373, 'insu_houseCooking': 1053, 'insu_heatFacility': 35481, 'insu_houseCHeating': 0, 'insu_sum': 193797, 'insu_salesOne': 6421, 'insu_bizCooling': 0, 'insu_heatCombined': 17, 'insu_industry': 108644}, '2019-08-29': {'insu_houseJHeating': 3462, 'insu_house': 429, 'insu_CNG': 23227, 'insu_bizHeating': 430, 'insu_salesTwo': 311, 'insu_houseCooking': 1314, 'insu_heatFacility': 24985, 'insu_houseCHeating': 0, 'insu_sum': 198529, 'insu_salesOne': 3794, 'insu_bizCooling': 2640, 'insu_heatCombined': 13415, 'insu_industry': 124521}, '2019-09-19': {'insu_houseJHeating': 4169, 'insu_house': 732, 'insu_CNG': 19938, 'insu_bizHeating': 434, 'insu_salesTwo': 255, 'insu_houseCooking': 1257, 'insu_heatFacility': 18219, 'insu_houseCHeating': 0, 'insu_sum': 163261, 'insu_salesOne': 2942, 'insu_bizCooling': 871, 'insu_heatCombined': 48, 'insu_industry': 114397}, '2019-01-02': {'insu_houseJHeating': 31471, 'insu_house': 5454, 'insu_CNG': 14191, 'insu_bizHeating': 6415, 'insu_salesTwo': 501, 'insu_houseCooking': 880, 'insu_heatFacility': 46140, 'insu_houseCHeating': 0, 'insu_sum': 224223, 'insu_salesOne': 6723, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 112446}, '2019-09-02': {'insu_houseJHeating': 3586, 'insu_house': 441, 'insu_CNG': 21601, 'insu_bizHeating': 635, 'insu_salesTwo': 366, 'insu_houseCooking': 1194, 'insu_heatFacility': 19739, 'insu_houseCHeating': 0, 'insu_sum': 176883, 'insu_salesOne': 4118, 'insu_bizCooling': 1278, 'insu_heatCombined': 52, 'insu_industry': 123874}, '2019-02-20': {'insu_houseJHeating': 39586, 'insu_house': 6712, 'insu_CNG': 18316, 'insu_bizHeating': 7567, 'insu_salesTwo': 659, 'insu_houseCooking': 1256, 'insu_heatFacility': 61748, 'insu_houseCHeating': 0, 'insu_sum': 273517, 'insu_salesOne': 8619, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 129055}, '2019-06-29': {'insu_houseJHeating': 4737, 'insu_house': 531, 'insu_CNG': 18191, 'insu_bizHeating': 640, 'insu_salesTwo': 202, 'insu_houseCooking': 1229, 'insu_heatFacility': 16471, 'insu_houseCHeating': 0, 'insu_sum': 159895, 'insu_salesOne': 3960, 'insu_bizCooling': 1595, 'insu_heatCombined': 10, 'insu_industry': 112330}, '2019-04-25': {'insu_houseJHeating': 17700, 'insu_house': 2452, 'insu_CNG': 23985, 'insu_bizHeating': 3493, 'insu_salesTwo': 445, 'insu_houseCooking': 1471, 'insu_heatFacility': 37896, 'insu_houseCHeating': 0, 'insu_sum': 267752, 'insu_salesOne': 7697, 'insu_bizCooling': 0, 'insu_heatCombined': 54, 'insu_industry': 172557}, '2019-08-24': {'insu_houseJHeating': 2739, 'insu_house': 339, 'insu_CNG': 18386, 'insu_bizHeating': 341, 'insu_salesTwo': 247, 'insu_houseCooking': 1041, 'insu_heatFacility': 19778, 'insu_houseCHeating': 0, 'insu_sum': 157153, 'insu_salesOne': 3001, 'insu_bizCooling': 2092, 'insu_heatCombined': 10619, 'insu_industry': 98569}, '2019-02-13': {'insu_houseJHeating': 40807, 'insu_house': 7541, 'insu_CNG': 18810, 'insu_bizHeating': 7641, 'insu_salesTwo': 645, 'insu_houseCooking': 1291, 'insu_heatFacility': 63411, 'insu_houseCHeating': 0, 'insu_sum': 280886, 'insu_salesOne': 8208, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 132532}, '2019-04-24': {'insu_houseJHeating': 13035, 'insu_house': 1806, 'insu_CNG': 17668, 'insu_bizHeating': 2579, 'insu_salesTwo': 329, 'insu_houseCooking': 1083, 'insu_heatFacility': 27916, 'insu_houseCHeating': 0, 'insu_sum': 197236, 'insu_salesOne': 5670, 'insu_bizCooling': 0, 'insu_heatCombined': 40, 'insu_industry': 127112}, '2019-01-30': {'insu_houseJHeating': 44236, 'insu_house': 8571, 'insu_CNG': 20148, 'insu_bizHeating': 8908, 'insu_salesTwo': 719, 'insu_houseCooking': 1409, 'insu_heatFacility': 65510, 'insu_houseCHeating': 0, 'insu_sum': 318354, 'insu_salesOne': 9197, 'insu_bizCooling': 0, 'insu_heatCombined': 4, 'insu_industry': 159651}, '2019-01-11': {'insu_houseJHeating': 41637, 'insu_house': 7459, 'insu_CNG': 18936, 'insu_bizHeating': 8564, 'insu_salesTwo': 669, 'insu_houseCooking': 1332, 'insu_heatFacility': 61569, 'insu_houseCHeating': 0, 'insu_sum': 299201, 'insu_salesOne': 8985, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 150046}, '2019-08-20': {'insu_houseJHeating': 2545, 'insu_house': 314, 'insu_CNG': 17101, 'insu_bizHeating': 319, 'insu_salesTwo': 231, 'insu_houseCooking': 971, 'insu_heatFacility': 18396, 'insu_houseCHeating': 0, 'insu_sum': 146173, 'insu_salesOne': 2777, 'insu_bizCooling': 1958, 'insu_heatCombined': 9877, 'insu_industry': 91683}, '2019-09-11': {'insu_houseJHeating': 3737, 'insu_house': 369, 'insu_CNG': 19503, 'insu_bizHeating': 510, 'insu_salesTwo': 294, 'insu_houseCooking': 1229, 'insu_heatFacility': 17822, 'insu_houseCHeating': 0, 'insu_sum': 159706, 'insu_salesOne': 3323, 'insu_bizCooling': 1027, 'insu_heatCombined': 47, 'insu_industry': 111845}, '2019-02-26': {'insu_houseJHeating': 28368, 'insu_house': 4764, 'insu_CNG': 13076, 'insu_bizHeating': 5339, 'insu_salesTwo': 464, 'insu_houseCooking': 894, 'insu_heatFacility': 44083, 'insu_houseCHeating': 0, 'insu_sum': 195270, 'insu_salesOne': 6147, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 92135}, '2019-03-08': {'insu_houseJHeating': 26239, 'insu_house': 5040, 'insu_CNG': 20352, 'insu_bizHeating': 5193, 'insu_salesTwo': 476, 'insu_houseCooking': 1373, 'insu_heatFacility': 46887, 'insu_houseCHeating': 0, 'insu_sum': 256098, 'insu_salesOne': 6945, 'insu_bizCooling': 0, 'insu_heatCombined': 22, 'insu_industry': 143571}, '2019-08-04': {'insu_houseJHeating': 2107, 'insu_house': 240, 'insu_CNG': 14083, 'insu_bizHeating': 247, 'insu_salesTwo': 176, 'insu_houseCooking': 838, 'insu_heatFacility': 15150, 'insu_houseCHeating': 0, 'insu_sum': 120378, 'insu_salesOne': 2357, 'insu_bizCooling': 1541, 'insu_heatCombined': 8134, 'insu_industry': 75503}, '2019-06-22': {'insu_houseJHeating': 4635, 'insu_house': 516, 'insu_CNG': 17277, 'insu_bizHeating': 671, 'insu_salesTwo': 196, 'insu_houseCooking': 1135, 'insu_heatFacility': 15643, 'insu_houseCHeating': 0, 'insu_sum': 151860, 'insu_salesOne': 3902, 'insu_bizCooling': 1184, 'insu_heatCombined': 16, 'insu_industry': 106685}, '2019-02-01': {'insu_houseJHeating': 43854, 'insu_house': 8470, 'insu_CNG': 20537, 'insu_bizHeating': 8621, 'insu_salesTwo': 737, 'insu_houseCooking': 1357, 'insu_heatFacility': 69235, 'insu_houseCHeating': 0, 'insu_sum': 306681, 'insu_salesOne': 9167, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 144703}, '2019-03-30': {'insu_houseJHeating': 22320, 'insu_house': 3561, 'insu_CNG': 17747, 'insu_bizHeating': 4514, 'insu_salesTwo': 433, 'insu_houseCooking': 1215, 'insu_heatFacility': 40887, 'insu_houseCHeating': 0, 'insu_sum': 223323, 'insu_salesOne': 7268, 'insu_bizCooling': 0, 'insu_heatCombined': 45, 'insu_industry': 125334}, '2019-02-07': {'insu_houseJHeating': 40582, 'insu_house': 7507, 'insu_CNG': 18635, 'insu_bizHeating': 7552, 'insu_salesTwo': 646, 'insu_houseCooking': 1174, 'insu_heatFacility': 62823, 'insu_houseCHeating': 0, 'insu_sum': 278279, 'insu_salesOne': 8059, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 131302}, '2019-02-18': {'insu_houseJHeating': 33104, 'insu_house': 5828, 'insu_CNG': 15285, 'insu_bizHeating': 6305, 'insu_salesTwo': 534, 'insu_houseCooking': 1048, 'insu_heatFacility': 51531, 'insu_houseCHeating': 0, 'insu_sum': 228260, 'insu_salesOne': 6924, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 107701}, '2019-01-08': {'insu_houseJHeating': 31328, 'insu_house': 5583, 'insu_CNG': 14166, 'insu_bizHeating': 6363, 'insu_salesTwo': 497, 'insu_houseCooking': 925, 'insu_heatFacility': 46058, 'insu_houseCHeating': 0, 'insu_sum': 223826, 'insu_salesOne': 6656, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 112246}, '2019-03-31': {'insu_houseJHeating': 13965, 'insu_house': 2284, 'insu_CNG': 11602, 'insu_bizHeating': 2658, 'insu_salesTwo': 279, 'insu_houseCooking': 794, 'insu_heatFacility': 26730, 'insu_houseCHeating': 0, 'insu_sum': 146000, 'insu_salesOne': 4735, 'insu_bizCooling': 0, 'insu_heatCombined': 30, 'insu_industry': 82922}, '2019-01-17': {'insu_houseJHeating': 37914, 'insu_house': 6890, 'insu_CNG': 17236, 'insu_bizHeating': 7743, 'insu_salesTwo': 615, 'insu_houseCooking': 1211, 'insu_heatFacility': 56042, 'insu_houseCHeating': 0, 'insu_sum': 272341, 'insu_salesOne': 8110, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 136576}, '2019-05-01': {'insu_houseJHeating': 9023, 'insu_house': 1299, 'insu_CNG': 16601, 'insu_bizHeating': 865, 'insu_salesTwo': 228, 'insu_houseCooking': 959, 'insu_heatFacility': 19173, 'insu_houseCHeating': 0, 'insu_sum': 174599, 'insu_salesOne': 3941, 'insu_bizCooling': 419, 'insu_heatCombined': 27, 'insu_industry': 122064}, '2019-05-14': {'insu_houseJHeating': 8540, 'insu_house': 1164, 'insu_CNG': 17050, 'insu_bizHeating': 1003, 'insu_salesTwo': 266, 'insu_houseCooking': 1036, 'insu_heatFacility': 19691, 'insu_houseCHeating': 0, 'insu_sum': 179325, 'insu_salesOne': 4689, 'insu_bizCooling': 489, 'insu_heatCombined': 28, 'insu_industry': 125368}, '2019-04-11': {'insu_houseJHeating': 15231, 'insu_house': 2728, 'insu_CNG': 19907, 'insu_bizHeating': 2536, 'insu_salesTwo': 326, 'insu_houseCooking': 1220, 'insu_heatFacility': 31453, 'insu_houseCHeating': 0, 'insu_sum': 222226, 'insu_salesOne': 5563, 'insu_bizCooling': 0, 'insu_heatCombined': 45, 'insu_industry': 143217}, '2019-07-17': {'insu_houseJHeating': 3211, 'insu_house': 412, 'insu_CNG': 17503, 'insu_bizHeating': 443, 'insu_salesTwo': 165, 'insu_houseCooking': 1030, 'insu_heatFacility': 19544, 'insu_houseCHeating': 0, 'insu_sum': 144308, 'insu_salesOne': 3456, 'insu_bizCooling': 1932, 'insu_heatCombined': 11, 'insu_industry': 96603}, '2019-03-25': {'insu_houseJHeating': 18293, 'insu_house': 2897, 'insu_CNG': 14796, 'insu_bizHeating': 4211, 'insu_salesTwo': 357, 'insu_houseCooking': 1012, 'insu_heatFacility': 34088, 'insu_houseCHeating': 0, 'insu_sum': 186187, 'insu_salesOne': 6139, 'insu_bizCooling': 0, 'insu_heatCombined': 16, 'insu_industry': 104378}, '2019-01-09': {'insu_houseJHeating': 39852, 'insu_house': 7197, 'insu_CNG': 18138, 'insu_bizHeating': 8200, 'insu_salesTwo': 640, 'insu_houseCooking': 1272, 'insu_heatFacility': 58975, 'insu_houseCHeating': 0, 'insu_sum': 286594, 'insu_salesOne': 8593, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 143724}, '2019-02-22': {'insu_houseJHeating': 39285, 'insu_house': 6648, 'insu_CNG': 18175, 'insu_bizHeating': 7468, 'insu_salesTwo': 650, 'insu_houseCooking': 1244, 'insu_heatFacility': 61273, 'insu_houseCHeating': 0, 'insu_sum': 271415, 'insu_salesOne': 8608, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 128063}, '2019-06-28': {'insu_houseJHeating': 6619, 'insu_house': 748, 'insu_CNG': 25472, 'insu_bizHeating': 902, 'insu_salesTwo': 284, 'insu_houseCooking': 1685, 'insu_heatFacility': 23064, 'insu_houseCHeating': 0, 'insu_sum': 223897, 'insu_salesOne': 5569, 'insu_bizCooling': 2248, 'insu_heatCombined': 13, 'insu_industry': 157292}, '2019-05-02': {'insu_houseJHeating': 9533, 'insu_house': 1383, 'insu_CNG': 17605, 'insu_bizHeating': 923, 'insu_salesTwo': 243, 'insu_houseCooking': 1017, 'insu_heatFacility': 20333, 'insu_houseCHeating': 0, 'insu_sum': 185163, 'insu_salesOne': 4202, 'insu_bizCooling': 447, 'insu_heatCombined': 29, 'insu_industry': 129449}, '2019-02-10': {'insu_houseJHeating': 37254, 'insu_house': 6865, 'insu_CNG': 17098, 'insu_bizHeating': 6876, 'insu_salesTwo': 588, 'insu_houseCooking': 1173, 'insu_heatFacility': 57640, 'insu_houseCHeating': 0, 'insu_sum': 255324, 'insu_salesOne': 7358, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 120471}, '2019-02-06': {'insu_houseJHeating': 50369, 'insu_house': 9328, 'insu_CNG': 23147, 'insu_bizHeating': 9372, 'insu_salesTwo': 802, 'insu_houseCooking': 1509, 'insu_heatFacility': 78033, 'insu_houseCHeating': 0, 'insu_sum': 345653, 'insu_salesOne': 10002, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 163092}, '2019-01-15': {'insu_houseJHeating': 30149, 'insu_house': 5422, 'insu_CNG': 13687, 'insu_bizHeating': 6150, 'insu_salesTwo': 480, 'insu_houseCooking': 963, 'insu_heatFacility': 44503, 'insu_houseCHeating': 0, 'insu_sum': 216269, 'insu_salesOne': 6455, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 108457}, '2019-03-24': {'insu_houseJHeating': 21297, 'insu_house': 3389, 'insu_CNG': 17247, 'insu_bizHeating': 4914, 'insu_salesTwo': 416, 'insu_houseCooking': 1180, 'insu_heatFacility': 39735, 'insu_houseCHeating': 0, 'insu_sum': 217030, 'insu_salesOne': 7164, 'insu_bizCooling': 0, 'insu_heatCombined': 19, 'insu_industry': 121669}, '2019-04-28': {'insu_houseJHeating': 11373, 'insu_house': 1586, 'insu_CNG': 15226, 'insu_bizHeating': 2071, 'insu_salesTwo': 286, 'insu_houseCooking': 933, 'insu_heatFacility': 24057, 'insu_houseCHeating': 0, 'insu_sum': 169973, 'insu_salesOne': 4873, 'insu_bizCooling': 0, 'insu_heatCombined': 27, 'insu_industry': 109542}, '2019-08-16': {'insu_houseJHeating': 2556, 'insu_house': 305, 'insu_CNG': 17681, 'insu_bizHeating': 319, 'insu_salesTwo': 228, 'insu_houseCooking': 1004, 'insu_heatFacility': 19020, 'insu_houseCHeating': 0, 'insu_sum': 151129, 'insu_salesOne': 3022, 'insu_bizCooling': 1991, 'insu_heatCombined': 10212, 'insu_industry': 94791}, '2019-01-13': {'insu_houseJHeating': 36213, 'insu_house': 6519, 'insu_CNG': 16456, 'insu_bizHeating': 7412, 'insu_salesTwo': 578, 'insu_houseCooking': 1157, 'insu_heatFacility': 53505, 'insu_houseCHeating': 0, 'insu_sum': 260014, 'insu_salesOne': 7777, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 130394}, '2019-07-12': {'insu_houseJHeating': 5306, 'insu_house': 639, 'insu_CNG': 26877, 'insu_bizHeating': 653, 'insu_salesTwo': 244, 'insu_houseCooking': 1592, 'insu_heatFacility': 30010, 'insu_houseCHeating': 0, 'insu_sum': 221590, 'insu_salesOne': 5069, 'insu_bizCooling': 2848, 'insu_heatCombined': 16, 'insu_industry': 148337}, '2019-05-04': {'insu_houseJHeating': 9510, 'insu_house': 1444, 'insu_CNG': 17860, 'insu_bizHeating': 960, 'insu_salesTwo': 252, 'insu_houseCooking': 995, 'insu_heatFacility': 20627, 'insu_houseCHeating': 0, 'insu_sum': 187846, 'insu_salesOne': 4379, 'insu_bizCooling': 465, 'insu_heatCombined': 29, 'insu_industry': 131325}, '2019-04-29': {'insu_houseJHeating': 12677, 'insu_house': 1768, 'insu_CNG': 16971, 'insu_bizHeating': 2308, 'insu_salesTwo': 319, 'insu_houseCooking': 1040, 'insu_heatFacility': 26814, 'insu_houseCHeating': 0, 'insu_sum': 189451, 'insu_salesOne': 5430, 'insu_bizCooling': 0, 'insu_heatCombined': 30, 'insu_industry': 122095}, '2019-01-01': {'insu_houseJHeating': 32590, 'insu_house': 5576, 'insu_CNG': 14636, 'insu_bizHeating': 6575, 'insu_salesTwo': 513, 'insu_houseCooking': 967, 'insu_heatFacility': 47589, 'insu_houseCHeating': 0, 'insu_sum': 231266, 'insu_salesOne': 6837, 'insu_bizCooling': 0, 'insu_heatCombined': 3, 'insu_industry': 115978}, '2019-03-04': {'insu_houseJHeating': 23397, 'insu_house': 4224, 'insu_CNG': 17736, 'insu_bizHeating': 4461, 'insu_salesTwo': 411, 'insu_houseCooking': 1002, 'insu_heatFacility': 40860, 'insu_houseCHeating': 0, 'insu_sum': 223178, 'insu_salesOne': 5954, 'insu_bizCooling': 0, 'insu_heatCombined': 19, 'insu_industry': 125115}, '2019-03-05': {'insu_houseJHeating': 20615, 'insu_house': 3820, 'insu_CNG': 15702, 'insu_bizHeating': 3950, 'insu_salesTwo': 364, 'insu_houseCooking': 888, 'insu_heatFacility': 36175, 'insu_houseCHeating': 0, 'insu_sum': 197585, 'insu_salesOne': 5286, 'insu_bizCooling': 0, 'insu_heatCombined': 17, 'insu_industry': 110768}, '2019-10-03': {'insu_houseJHeating': 12129, 'insu_house': 2092, 'insu_CNG': 20317, 'insu_bizHeating': 3021, 'insu_salesTwo': 726, 'insu_houseCooking': 1590, 'insu_heatFacility': 24876, 'insu_houseCHeating': 0, 'insu_sum': 213353, 'insu_salesOne': 8446, 'insu_bizCooling': 0, 'insu_heatCombined': 62, 'insu_industry': 140094}, '2019-05-06': {'insu_houseJHeating': 6609, 'insu_house': 1038, 'insu_CNG': 12631, 'insu_bizHeating': 690, 'insu_salesTwo': 181, 'insu_houseCooking': 731, 'insu_heatFacility': 14588, 'insu_houseCHeating': 0, 'insu_sum': 132847, 'insu_salesOne': 3149, 'insu_bizCooling': 334, 'insu_heatCombined': 21, 'insu_industry': 92875}, '2019-05-30': {'insu_houseJHeating': 8021, 'insu_house': 922, 'insu_CNG': 16852, 'insu_bizHeating': 969, 'insu_salesTwo': 290, 'insu_houseCooking': 1020, 'insu_heatFacility': 19463, 'insu_houseCHeating': 0, 'insu_sum': 177242, 'insu_salesOne': 5107, 'insu_bizCooling': 669, 'insu_heatCombined': 18, 'insu_industry': 123911}, '2019-03-22': {'insu_houseJHeating': 26312, 'insu_house': 4192, 'insu_CNG': 21334, 'insu_bizHeating': 6093, 'insu_salesTwo': 516, 'insu_houseCooking': 1459, 'insu_heatFacility': 49151, 'insu_houseCHeating': 0, 'insu_sum': 268460, 'insu_salesOne': 8878, 'insu_bizCooling': 0, 'insu_heatCombined': 23, 'insu_industry': 150501}, '2019-06-15': {'insu_houseJHeating': 4811, 'insu_house': 600, 'insu_CNG': 17892, 'insu_bizHeating': 690, 'insu_salesTwo': 195, 'insu_houseCooking': 1168, 'insu_heatFacility': 16201, 'insu_houseCHeating': 0, 'insu_sum': 157270, 'insu_salesOne': 4005, 'insu_bizCooling': 1206, 'insu_heatCombined': 16, 'insu_industry': 110486}, '2019-09-25': {'insu_houseJHeating': 2789, 'insu_house': 489, 'insu_CNG': 13312, 'insu_bizHeating': 289, 'insu_salesTwo': 170, 'insu_houseCooking': 839, 'insu_heatFacility': 12164, 'insu_houseCHeating': 0, 'insu_sum': 109003, 'insu_salesOne': 1961, 'insu_bizCooling': 580, 'insu_heatCombined': 32, 'insu_industry': 76378}, '2019-07-15': {'insu_houseJHeating': 4339, 'insu_house': 517, 'insu_CNG': 22274, 'insu_bizHeating': 546, 'insu_salesTwo': 204, 'insu_houseCooking': 1310, 'insu_heatFacility': 24871, 'insu_houseCHeating': 0, 'insu_sum': 183642, 'insu_salesOne': 4252, 'insu_bizCooling': 2382, 'insu_heatCombined': 13, 'insu_industry': 122934}, '2019-10-05': {'insu_houseJHeating': 10092, 'insu_house': 1687, 'insu_CNG': 16497, 'insu_bizHeating': 2399, 'insu_salesTwo': 576, 'insu_houseCooking': 1280, 'insu_heatFacility': 20199, 'insu_houseCHeating': 0, 'insu_sum': 173237, 'insu_salesOne': 6705, 'insu_bizCooling': 0, 'insu_heatCombined': 50, 'insu_industry': 113752}, '2019-07-29': {'insu_houseJHeating': 3269, 'insu_house': 356, 'insu_CNG': 17830, 'insu_bizHeating': 380, 'insu_salesTwo': 159, 'insu_houseCooking': 1039, 'insu_heatFacility': 19909, 'insu_houseCHeating': 0, 'insu_sum': 147007, 'insu_salesOne': 3555, 'insu_bizCooling': 2096, 'insu_heatCombined': 6, 'insu_industry': 98406}, '2019-06-14': {'insu_houseJHeating': 5384, 'insu_house': 716, 'insu_CNG': 19881, 'insu_bizHeating': 761, 'insu_salesTwo': 216, 'insu_houseCooking': 1297, 'insu_heatFacility': 18001, 'insu_houseCHeating': 0, 'insu_sum': 174749, 'insu_salesOne': 4380, 'insu_bizCooling': 1330, 'insu_heatCombined': 18, 'insu_industry': 122765}, '2019-05-17': {'insu_houseJHeating': 10621, 'insu_house': 1190, 'insu_CNG': 22216, 'insu_bizHeating': 1369, 'insu_salesTwo': 384, 'insu_houseCooking': 1349, 'insu_heatFacility': 25657, 'insu_houseCHeating': 0, 'insu_sum': 233654, 'insu_salesOne': 6793, 'insu_bizCooling': 688, 'insu_heatCombined': 37, 'insu_industry': 163350}, '2019-07-01': {'insu_houseJHeating': 4322, 'insu_house': 495, 'insu_CNG': 20317, 'insu_bizHeating': 468, 'insu_salesTwo': 175, 'insu_houseCooking': 1287, 'insu_heatFacility': 22686, 'insu_houseCHeating': 0, 'insu_sum': 167508, 'insu_salesOne': 3614, 'insu_bizCooling': 2002, 'insu_heatCombined': 10, 'insu_industry': 112133}, '2019-04-18': {'insu_houseJHeating': 15430, 'insu_house': 2144, 'insu_CNG': 20889, 'insu_bizHeating': 3069, 'insu_salesTwo': 391, 'insu_houseCooking': 1280, 'insu_heatFacility': 33005, 'insu_houseCHeating': 0, 'insu_sum': 233196, 'insu_salesOne': 6652, 'insu_bizCooling': 0, 'insu_heatCombined': 47, 'insu_industry': 150287}, '2019-02-11': {'insu_houseJHeating': 41698, 'insu_house': 7640, 'insu_CNG': 19125, 'insu_bizHeating': 7694, 'insu_salesTwo': 658, 'insu_houseCooking': 1313, 'insu_heatFacility': 64476, 'insu_houseCHeating': 0, 'insu_sum': 285603, 'insu_salesOne': 8242, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 134758}, '2019-04-10': {'insu_houseJHeating': 13263, 'insu_house': 2370, 'insu_CNG': 17328, 'insu_bizHeating': 2208, 'insu_salesTwo': 284, 'insu_houseCooking': 1062, 'insu_heatFacility': 27379, 'insu_houseCHeating': 0, 'insu_sum': 193441, 'insu_salesOne': 4841, 'insu_bizCooling': 0, 'insu_heatCombined': 39, 'insu_industry': 124666}, '2019-07-04': {'insu_houseJHeating': 3886, 'insu_house': 454, 'insu_CNG': 18406, 'insu_bizHeating': 427, 'insu_salesTwo': 159, 'insu_houseCooking': 1074, 'insu_heatFacility': 20552, 'insu_houseCHeating': 0, 'insu_sum': 151751, 'insu_salesOne': 3334, 'insu_bizCooling': 1864, 'insu_heatCombined': 9, 'insu_industry': 101585}, '2019-06-11': {'insu_houseJHeating': 4718, 'insu_house': 625, 'insu_CNG': 16385, 'insu_bizHeating': 586, 'insu_salesTwo': 167, 'insu_houseCooking': 1112, 'insu_heatFacility': 14836, 'insu_houseCHeating': 0, 'insu_sum': 144019, 'insu_salesOne': 3374, 'insu_bizCooling': 1025, 'insu_heatCombined': 15, 'insu_industry': 101176}, '2019-08-28': {'insu_houseJHeating': 3041, 'insu_house': 377, 'insu_CNG': 20408, 'insu_bizHeating': 378, 'insu_salesTwo': 273, 'insu_houseCooking': 1155, 'insu_heatFacility': 21953, 'insu_houseCHeating': 0, 'insu_sum': 174433, 'insu_salesOne': 3333, 'insu_bizCooling': 2320, 'insu_heatCombined': 11787, 'insu_industry': 109408}, '2019-04-17': {'insu_houseJHeating': 11482, 'insu_house': 1711, 'insu_CNG': 15713, 'insu_bizHeating': 2276, 'insu_salesTwo': 287, 'insu_houseCooking': 964, 'insu_heatFacility': 24827, 'insu_houseCHeating': 0, 'insu_sum': 175410, 'insu_salesOne': 5068, 'insu_bizCooling': 0, 'insu_heatCombined': 36, 'insu_industry': 113046}, '2019-02-24': {'insu_houseJHeating': 32274, 'insu_house': 5446, 'insu_CNG': 14896, 'insu_bizHeating': 6092, 'insu_salesTwo': 530, 'insu_houseCooking': 1020, 'insu_heatFacility': 50217, 'insu_houseCHeating': 0, 'insu_sum': 222439, 'insu_salesOne': 7010, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 104955}, '2019-04-16': {'insu_houseJHeating': 11238, 'insu_house': 1785, 'insu_CNG': 15434, 'insu_bizHeating': 2218, 'insu_salesTwo': 279, 'insu_houseCooking': 947, 'insu_heatFacility': 24385, 'insu_houseCHeating': 0, 'insu_sum': 172292, 'insu_salesOne': 4935, 'insu_bizCooling': 0, 'insu_heatCombined': 35, 'insu_industry': 111037}, '2019-04-19': {'insu_houseJHeating': 14011, 'insu_house': 1947, 'insu_CNG': 18964, 'insu_bizHeating': 2786, 'insu_salesTwo': 355, 'insu_houseCooking': 1162, 'insu_heatFacility': 29963, 'insu_houseCHeating': 0, 'insu_sum': 211700, 'insu_salesOne': 6037, 'insu_bizCooling': 0, 'insu_heatCombined': 43, 'insu_industry': 136434}, '2019-10-06': {'insu_houseJHeating': 9161, 'insu_house': 1503, 'insu_CNG': 14757, 'insu_bizHeating': 2133, 'insu_salesTwo': 513, 'insu_houseCooking': 1053, 'insu_heatFacility': 18068, 'insu_houseCHeating': 0, 'insu_sum': 154962, 'insu_salesOne': 5978, 'insu_bizCooling': 0, 'insu_heatCombined': 45, 'insu_industry': 101752}, '2019-08-18': {'insu_houseJHeating': 2629, 'insu_house': 322, 'insu_CNG': 17812, 'insu_bizHeating': 325, 'insu_salesTwo': 232, 'insu_houseCooking': 1012, 'insu_heatFacility': 19161, 'insu_houseCHeating': 0, 'insu_sum': 152249, 'insu_salesOne': 2949, 'insu_bizCooling': 2025, 'insu_heatCombined': 10288, 'insu_industry': 95494}, '2019-06-30': {'insu_houseJHeating': 3934, 'insu_house': 441, 'insu_CNG': 14222, 'insu_bizHeating': 510, 'insu_salesTwo': 155, 'insu_houseCooking': 961, 'insu_heatFacility': 12877, 'insu_houseCHeating': 0, 'insu_sum': 125005, 'insu_salesOne': 3267, 'insu_bizCooling': 1593, 'insu_heatCombined': 7, 'insu_industry': 87039}, '2019-09-10': {'insu_houseJHeating': 3607, 'insu_house': 367, 'insu_CNG': 19126, 'insu_bizHeating': 508, 'insu_salesTwo': 292, 'insu_houseCooking': 1181, 'insu_heatFacility': 17477, 'insu_houseCHeating': 0, 'insu_sum': 156617, 'insu_salesOne': 3308, 'insu_bizCooling': 1022, 'insu_heatCombined': 46, 'insu_industry': 109681}, '2019-04-21': {'insu_houseJHeating': 11096, 'insu_house': 1538, 'insu_CNG': 15050, 'insu_bizHeating': 2201, 'insu_salesTwo': 280, 'insu_houseCooking': 923, 'insu_heatFacility': 23780, 'insu_houseCHeating': 0, 'insu_sum': 168014, 'insu_salesOne': 4832, 'insu_bizCooling': 0, 'insu_heatCombined': 34, 'insu_industry': 108280}, '2019-09-23': {'insu_houseJHeating': 4080, 'insu_house': 716, 'insu_CNG': 19474, 'insu_bizHeating': 423, 'insu_salesTwo': 249, 'insu_houseCooking': 1227, 'insu_heatFacility': 17796, 'insu_houseCHeating': 0, 'insu_sum': 159469, 'insu_salesOne': 2869, 'insu_bizCooling': 849, 'insu_heatCombined': 47, 'insu_industry': 111740}, '2019-02-08': {'insu_houseJHeating': 45449, 'insu_house': 8393, 'insu_CNG': 20847, 'insu_bizHeating': 8424, 'insu_salesTwo': 720, 'insu_houseCooking': 1321, 'insu_heatFacility': 70280, 'insu_houseCHeating': 0, 'insu_sum': 311314, 'insu_salesOne': 8990, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 146889}, '2019-09-14': {'insu_houseJHeating': 4007, 'insu_house': 439, 'insu_CNG': 19079, 'insu_bizHeating': 446, 'insu_salesTwo': 256, 'insu_houseCooking': 1203, 'insu_heatFacility': 17434, 'insu_houseCHeating': 0, 'insu_sum': 156232, 'insu_salesOne': 2954, 'insu_bizCooling': 896, 'insu_heatCombined': 46, 'insu_industry': 109471}, '2019-05-16': {'insu_houseJHeating': 8076, 'insu_house': 1017, 'insu_CNG': 16950, 'insu_bizHeating': 1050, 'insu_salesTwo': 284, 'insu_houseCooking': 1029, 'insu_heatFacility': 19576, 'insu_houseCHeating': 0, 'insu_sum': 178275, 'insu_salesOne': 5109, 'insu_bizCooling': 522, 'insu_heatCombined': 28, 'insu_industry': 124634}, '2019-06-20': {'insu_houseJHeating': 4877, 'insu_house': 544, 'insu_CNG': 18207, 'insu_bizHeating': 708, 'insu_salesTwo': 207, 'insu_houseCooking': 1197, 'insu_heatFacility': 16486, 'insu_houseCHeating': 0, 'insu_sum': 160037, 'insu_salesOne': 4114, 'insu_bizCooling': 1251, 'insu_heatCombined': 17, 'insu_industry': 112429}, '2019-08-15': {'insu_houseJHeating': 2287, 'insu_house': 285, 'insu_CNG': 15868, 'insu_bizHeating': 286, 'insu_salesTwo': 204, 'insu_houseCooking': 901, 'insu_heatFacility': 17069, 'insu_houseCHeating': 0, 'insu_sum': 135629, 'insu_salesOne': 2712, 'insu_bizCooling': 1783, 'insu_heatCombined': 9165, 'insu_industry': 85069}, '2019-06-25': {'insu_houseJHeating': 4667, 'insu_house': 523, 'insu_CNG': 17445, 'insu_bizHeating': 679, 'insu_salesTwo': 198, 'insu_houseCooking': 1144, 'insu_heatFacility': 15796, 'insu_houseCHeating': 0, 'insu_sum': 153339, 'insu_salesOne': 3948, 'insu_bizCooling': 1199, 'insu_heatCombined': 16, 'insu_industry': 107724}, '2019-04-22': {'insu_houseJHeating': 14215, 'insu_house': 1972, 'insu_CNG': 19281, 'insu_bizHeating': 2819, 'insu_salesTwo': 359, 'insu_houseCooking': 1182, 'insu_heatFacility': 30465, 'insu_houseCHeating': 0, 'insu_sum': 215246, 'insu_salesOne': 6190, 'insu_bizCooling': 0, 'insu_heatCombined': 44, 'insu_industry': 138719}, '2019-08-26': {'insu_houseJHeating': 3583, 'insu_house': 444, 'insu_CNG': 24040, 'insu_bizHeating': 446, 'insu_salesTwo': 322, 'insu_houseCooking': 1360, 'insu_heatFacility': 25860, 'insu_houseCHeating': 0, 'insu_sum': 205482, 'insu_salesOne': 3923, 'insu_bizCooling': 2736, 'insu_heatCombined': 13885, 'insu_industry': 128882}, '2019-03-03': {'insu_houseJHeating': 22758, 'insu_house': 4101, 'insu_CNG': 17248, 'insu_bizHeating': 4330, 'insu_salesTwo': 399, 'insu_houseCooking': 994, 'insu_heatFacility': 39736, 'insu_houseCHeating': 0, 'insu_sum': 217036, 'insu_salesOne': 5780, 'insu_bizCooling': 0, 'insu_heatCombined': 19, 'insu_industry': 121672}, '2019-05-03': {'insu_houseJHeating': 12539, 'insu_house': 1837, 'insu_CNG': 23227, 'insu_bizHeating': 1221, 'insu_salesTwo': 321, 'insu_houseCooking': 1339, 'insu_heatFacility': 26825, 'insu_houseCHeating': 0, 'insu_sum': 244287, 'insu_salesOne': 5566, 'insu_bizCooling': 591, 'insu_heatCombined': 38, 'insu_industry': 170783}, '2019-03-18': {'insu_houseJHeating': 22117, 'insu_house': 3652, 'insu_CNG': 17956, 'insu_bizHeating': 5187, 'insu_salesTwo': 427, 'insu_houseCooking': 1228, 'insu_heatFacility': 41368, 'insu_houseCHeating': 0, 'insu_sum': 225950, 'insu_salesOne': 7326, 'insu_bizCooling': 0, 'insu_heatCombined': 19, 'insu_industry': 126669}, '2019-03-15': {'insu_houseJHeating': 17570, 'insu_house': 3204, 'insu_CNG': 14307, 'insu_bizHeating': 4077, 'insu_salesTwo': 334, 'insu_houseCooking': 979, 'insu_heatFacility': 32962, 'insu_houseCHeating': 0, 'insu_sum': 180038, 'insu_salesOne': 5658, 'insu_bizCooling': 0, 'insu_heatCombined': 15, 'insu_industry': 100931}, '2019-07-30': {'insu_houseJHeating': 3132, 'insu_house': 341, 'insu_CNG': 17115, 'insu_bizHeating': 364, 'insu_salesTwo': 152, 'insu_houseCooking': 997, 'insu_heatFacility': 19110, 'insu_houseCHeating': 0, 'insu_sum': 141107, 'insu_salesOne': 3425, 'insu_bizCooling': 2007, 'insu_heatCombined': 6, 'insu_industry': 94457}, '2019-02-23': {'insu_houseJHeating': 35508, 'insu_house': 6018, 'insu_CNG': 16420, 'insu_bizHeating': 6739, 'insu_salesTwo': 586, 'insu_houseCooking': 1125, 'insu_heatFacility': 55354, 'insu_houseCHeating': 0, 'insu_sum': 245196, 'insu_salesOne': 7754, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 115692}, '2019-03-17': {'insu_houseJHeating': 19473, 'insu_house': 3420, 'insu_CNG': 15826, 'insu_bizHeating': 4537, 'insu_salesTwo': 371, 'insu_houseCooking': 1083, 'insu_heatFacility': 36460, 'insu_houseCHeating': 0, 'insu_sum': 199145, 'insu_salesOne': 6315, 'insu_bizCooling': 0, 'insu_heatCombined': 17, 'insu_industry': 111642}, '2019-04-08': {'insu_houseJHeating': 13918, 'insu_house': 2479, 'insu_CNG': 18164, 'insu_bizHeating': 2312, 'insu_salesTwo': 297, 'insu_houseCooking': 1109, 'insu_heatFacility': 28699, 'insu_houseCHeating': 0, 'insu_sum': 202767, 'insu_salesOne': 5071, 'insu_bizCooling': 0, 'insu_heatCombined': 41, 'insu_industry': 130677}, '2019-09-04': {'insu_houseJHeating': 3343, 'insu_house': 387, 'insu_CNG': 19377, 'insu_bizHeating': 555, 'insu_salesTwo': 320, 'insu_houseCooking': 1077, 'insu_heatFacility': 17707, 'insu_houseCHeating': 0, 'insu_sum': 158674, 'insu_salesOne': 3620, 'insu_bizCooling': 1118, 'insu_heatCombined': 46, 'insu_industry': 111122}, '2019-05-07': {'insu_houseJHeating': 10611, 'insu_house': 1670, 'insu_CNG': 20297, 'insu_bizHeating': 1110, 'insu_salesTwo': 292, 'insu_houseCooking': 1175, 'insu_heatFacility': 23442, 'insu_houseCHeating': 0, 'insu_sum': 213478, 'insu_salesOne': 5066, 'insu_bizCooling': 538, 'insu_heatCombined': 33, 'insu_industry': 149244}, '2019-06-21': {'insu_houseJHeating': 5981, 'insu_house': 666, 'insu_CNG': 22321, 'insu_bizHeating': 867, 'insu_salesTwo': 253, 'insu_houseCooking': 1467, 'insu_heatFacility': 20211, 'insu_houseCHeating': 0, 'insu_sum': 196202, 'insu_salesOne': 5049, 'insu_bizCooling': 1530, 'insu_heatCombined': 20, 'insu_industry': 137836}, '2019-08-19': {'insu_houseJHeating': 1702, 'insu_house': 209, 'insu_CNG': 11492, 'insu_bizHeating': 211, 'insu_salesTwo': 150, 'insu_houseCooking': 652, 'insu_heatFacility': 12362, 'insu_houseCHeating': 0, 'insu_sum': 98227, 'insu_salesOne': 1892, 'insu_bizCooling': 1310, 'insu_heatCombined': 6637, 'insu_industry': 61610}, '2019-07-19': {'insu_houseJHeating': 3217, 'insu_house': 350, 'insu_CNG': 17661, 'insu_bizHeating': 450, 'insu_salesTwo': 156, 'insu_houseCooking': 1039, 'insu_heatFacility': 19719, 'insu_houseCHeating': 0, 'insu_sum': 145606, 'insu_salesOne': 3556, 'insu_bizCooling': 1976, 'insu_heatCombined': 11, 'insu_industry': 97472}, '2019-06-06': {'insu_houseJHeating': 6892, 'insu_house': 839, 'insu_CNG': 22623, 'insu_bizHeating': 816, 'insu_salesTwo': 233, 'insu_houseCooking': 1159, 'insu_heatFacility': 20484, 'insu_houseCHeating': 0, 'insu_sum': 198849, 'insu_salesOne': 4661, 'insu_bizCooling': 1426, 'insu_heatCombined': 21, 'insu_industry': 139696}, '2019-04-07': {'insu_houseJHeating': 14517, 'insu_house': 2583, 'insu_CNG': 18938, 'insu_bizHeating': 2410, 'insu_salesTwo': 310, 'insu_houseCooking': 1157, 'insu_heatFacility': 29922, 'insu_houseCHeating': 0, 'insu_sum': 211407, 'insu_salesOne': 5284, 'insu_bizCooling': 0, 'insu_heatCombined': 43, 'insu_industry': 136245}, '2019-09-29': {'insu_houseJHeating': 3490, 'insu_house': 616, 'insu_CNG': 14325, 'insu_bizHeating': 543, 'insu_salesTwo': 216, 'insu_houseCooking': 902, 'insu_heatFacility': 13090, 'insu_houseCHeating': 0, 'insu_sum': 117305, 'insu_salesOne': 2483, 'insu_bizCooling': 450, 'insu_heatCombined': 49, 'insu_industry': 81140}, '2019-07-21': {'insu_houseJHeating': 2530, 'insu_house': 275, 'insu_CNG': 13889, 'insu_bizHeating': 354, 'insu_salesTwo': 123, 'insu_houseCooking': 817, 'insu_heatFacility': 15508, 'insu_houseCHeating': 0, 'insu_sum': 114508, 'insu_salesOne': 2797, 'insu_bizCooling': 1554, 'insu_heatCombined': 8, 'insu_industry': 76654}, '2019-06-08': {'insu_houseJHeating': 4775, 'insu_house': 608, 'insu_CNG': 16065, 'insu_bizHeating': 570, 'insu_salesTwo': 162, 'insu_houseCooking': 989, 'insu_heatFacility': 14546, 'insu_houseCHeating': 0, 'insu_sum': 141206, 'insu_salesOne': 3279, 'insu_bizCooling': 997, 'insu_heatCombined': 15, 'insu_industry': 99200}, '2019-06-07': {'insu_houseJHeating': 5082, 'insu_house': 646, 'insu_CNG': 16942, 'insu_bizHeating': 606, 'insu_salesTwo': 173, 'insu_houseCooking': 952, 'insu_heatFacility': 15340, 'insu_houseCHeating': 0, 'insu_sum': 148915, 'insu_salesOne': 3484, 'insu_bizCooling': 1059, 'insu_heatCombined': 15, 'insu_industry': 104616}, '2019-08-21': {'insu_houseJHeating': 2621, 'insu_house': 324, 'insu_CNG': 17606, 'insu_bizHeating': 329, 'insu_salesTwo': 238, 'insu_houseCooking': 999, 'insu_heatFacility': 18939, 'insu_houseCHeating': 0, 'insu_sum': 150488, 'insu_salesOne': 2859, 'insu_bizCooling': 2016, 'insu_heatCombined': 10169, 'insu_industry': 94389}, '2019-07-03': {'insu_houseJHeating': 3807, 'insu_house': 440, 'insu_CNG': 17941, 'insu_bizHeating': 415, 'insu_salesTwo': 155, 'insu_houseCooking': 1048, 'insu_heatFacility': 20033, 'insu_houseCHeating': 0, 'insu_sum': 147918, 'insu_salesOne': 3240, 'insu_bizCooling': 1812, 'insu_heatCombined': 9, 'insu_industry': 99019}, '2019-03-07': {'insu_houseJHeating': 24169, 'insu_house': 4632, 'insu_CNG': 18719, 'insu_bizHeating': 4788, 'insu_salesTwo': 439, 'insu_houseCooking': 1215, 'insu_heatFacility': 43126, 'insu_houseCHeating': 0, 'insu_sum': 235555, 'insu_salesOne': 6391, 'insu_bizCooling': 0, 'insu_heatCombined': 20, 'insu_industry': 132054}, '2019-04-13': {'insu_houseJHeating': 12351, 'insu_house': 1831, 'insu_CNG': 16092, 'insu_bizHeating': 2153, 'insu_salesTwo': 269, 'insu_houseCooking': 986, 'insu_heatFacility': 25425, 'insu_houseCHeating': 0, 'insu_sum': 179636, 'insu_salesOne': 4724, 'insu_bizCooling': 0, 'insu_heatCombined': 36, 'insu_industry': 115770}, '2019-06-13': {'insu_houseJHeating': 5550, 'insu_house': 726, 'insu_CNG': 19853, 'insu_bizHeating': 738, 'insu_salesTwo': 210, 'insu_houseCooking': 1301, 'insu_heatFacility': 17976, 'insu_houseCHeating': 0, 'insu_sum': 174508, 'insu_salesOne': 4249, 'insu_bizCooling': 1290, 'insu_heatCombined': 18, 'insu_industry': 122596}, '2019-03-26': {'insu_houseJHeating': 20163, 'insu_house': 3192, 'insu_CNG': 16302, 'insu_bizHeating': 4635, 'insu_salesTwo': 393, 'insu_houseCooking': 1116, 'insu_heatFacility': 37556, 'insu_houseCHeating': 0, 'insu_sum': 205132, 'insu_salesOne': 6758, 'insu_bizCooling': 0, 'insu_heatCombined': 18, 'insu_industry': 114999}, '2019-07-09': {'insu_houseJHeating': 3539, 'insu_house': 443, 'insu_CNG': 17468, 'insu_bizHeating': 416, 'insu_salesTwo': 155, 'insu_houseCooking': 1015, 'insu_heatFacility': 19505, 'insu_houseCHeating': 0, 'insu_sum': 144020, 'insu_salesOne': 3245, 'insu_bizCooling': 1814, 'insu_heatCombined': 11, 'insu_industry': 96410}, '2019-09-01': {'insu_houseJHeating': 2285, 'insu_house': 281, 'insu_CNG': 13756, 'insu_bizHeating': 405, 'insu_salesTwo': 233, 'insu_houseCooking': 747, 'insu_heatFacility': 12570, 'insu_houseCHeating': 0, 'insu_sum': 112640, 'insu_salesOne': 2631, 'insu_bizCooling': 815, 'insu_heatCombined': 33, 'insu_industry': 78884}, '2019-08-14': {'insu_houseJHeating': 2283, 'insu_house': 284, 'insu_CNG': 15848, 'insu_bizHeating': 286, 'insu_salesTwo': 204, 'insu_houseCooking': 896, 'insu_heatFacility': 17047, 'insu_houseCHeating': 0, 'insu_sum': 135456, 'insu_salesOne': 2716, 'insu_bizCooling': 1780, 'insu_heatCombined': 9153, 'insu_industry': 84961}, '2019-01-31': {'insu_houseJHeating': 44458, 'insu_house': 8617, 'insu_CNG': 20195, 'insu_bizHeating': 8759, 'insu_salesTwo': 721, 'insu_houseCooking': 1412, 'insu_heatFacility': 65664, 'insu_houseCHeating': 0, 'insu_sum': 319101, 'insu_salesOne': 9264, 'insu_bizCooling': 0, 'insu_heatCombined': 4, 'insu_industry': 160007}, '2019-02-25': {'insu_houseJHeating': 34599, 'insu_house': 5821, 'insu_CNG': 15957, 'insu_bizHeating': 6524, 'insu_salesTwo': 567, 'insu_houseCooking': 1092, 'insu_heatFacility': 53796, 'insu_houseCHeating': 0, 'insu_sum': 238296, 'insu_salesOne': 7503, 'insu_bizCooling': 0, 'insu_heatCombined': 0, 'insu_industry': 112437}}
                    # # final_result = {"2019-03-12": [{"insu_houseJHeating": 20191, "insu_house": 4068}]}
                    # for x, y in final_result.items():
                    #     tqq.append(x)
                    # tqq = sorted(tqq)


        # meta_get.update({str(area).upper() + '.' + str(resource):{"beginData": tqq[0], "endDate": tqq[-1]}})
        # meta = {}
        # meta["meta"]=meta_get
        # final_result2.update(meta)

        # ss = {}
        # ss[str(area).upper() + '.' + str(resource)] = final_result
        # final_result2.update(ss)




# @data_apis.route('/datasets123123', methods=['GET', 'POST'])
# def api_data_search_all123123():
#     try:
#         key = session['logger']
#         pkey = db_session.query(Login.pkey).filter(Login.id == str(key))
#         login = db_session.query(Login).get(pkey)
#     except:
#         pkey = 0
#     else:
#         pkey = login.pkey
#
#     req = request.get_json()
#     jsonString = json.dumps(req)
#     data = json.loads(jsonString)
#
#     try:
#         period = data['period']
#         ## 날짜시간 [2018, 3, 10, 1, 0, 0, 2019, 3, 6, 1, 0, 0] -> 리스트 len = 12
#         period_value = get_period_value(str(period))
#         print(period_value)
#         # datestart = '%04d-%02d-%02d' % (period_value[0], period_value[1], period_value[2])
#         dateend = int('%04d' % (period_value[6]))
#         datestart = int('%04d' % (period_value[0]))
#
#         datelist = []
#         for i in range(dateend - datestart + 1):
#             datestart += i
#             datelist.append(datestart)
#
#     except:
#         period = None
#
#     try:
#         dataset = data['dataset']
#     except Exception as e:
#         print('212: ', e)
#         abort(400)
#
#     final_result2 = dict()
#     meta_get = {}
#     # print(dataset)
#     for data in dataset:
#         final_result = dict()
#         # print("data: ",data)
#
#         try:
#             argument = data['arguments']
#             resource = argument['resource']
#             area = argument['location']
#
#             ## 지역이 나주가 아니면 naju로 강제 변환.
#             if not area == 'naju':
#                 area = 'naju'
#
#         except Exception as e:
#             print(e)
#             return abort(400)
#
#         else:
#             dataname = str()
#             # print(resource.count('.'))
#             if resource.count('.') == 1:
#                 for ddstart in datelist:
#                     path = folder_path + 'data/insu/%s_insu_%d' % (area.lower(), ddstart)
#                     print(path)
#
#                     ## '/home/uk/PredictionServer/prediction/prediction_ETRI/data/insu/naju_insu_2019'
#                     with open(path, 'r') as f:
#                         dataname = f.readline().strip()
#
#                     dataname = dataname.replace('\t', ' ')
#                     dataname = dataname.split(" ")[3:]
#
#                     print(dataname)
#
#                     pddata = pd.read_csv(path, delim_whitespace=True)
#                     data1 = "year month date"
#
#                     for index, row in sorted(pddata.iterrows()):
#
#                         yearmonthday = []
#                         # datavalue1_str = str()
#
#                         ## 각 날짜에 대한 년,월,일 값 가져옴.
#                         for i in data1.split(" "):
#                             yearmonthday.append(row[i])
#
#                         yearmonthday_str = '%04d-%02d-%02d' % (yearmonthday[0], yearmonthday[1], yearmonthday[2])
#
#                         file_datavalue = {}
#                         for i in dataname:
#                             file_datavalue.update({i: row[i]})
#
#                         # print(len(dataname))
#                         # print(len(datavalue2))
#
#                         # temp_list = [date]
#
#                         # qwe = dict(zip(dataname, datavalue2))
#
#                         kk = {}
#                         kk[yearmonthday_str] = file_datavalue
#                         final_result.update(kk)
#
#             # print(final_result)
#             # from API.DataSet.data_insu import data_insu
#             # final_result = data_insu(datestart)
#
#         tqq = []
#
#         # final_result = {"2019-03-12": [{"insu_houseJHeating": 20191, "insu_house": 4068}]}
#         for x, y in final_result.items():
#             tqq.append(x)
#         tqq = sorted(tqq)
#
#         meta_get.update({str(area).upper() + '.' + str(resource): {"beginData": tqq[0], "endDate": tqq[-1]}})
#         meta = {}
#         meta["meta"] = meta_get
#         final_result2.update(meta)
#
#         ss = {}
#         ss[str(area).upper() + '.' + str(resource)] = final_result
#         final_result2.update(ss)
#
#     return jsonify(final_result2)
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