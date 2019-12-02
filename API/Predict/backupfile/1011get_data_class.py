# -*- coding: utf-8 -*-
# set에서 받은 데이터를 API로 리턴.

'''general'''
import os
import sys
from datetime import datetime, date, time
import random
'''library'''
import pandas as pd
import numpy as np
'''directory'''
from API.Predict.set_data_class import set_predic_data
from API.api_helper.user_directory import folder_path, folder_path2
from API.api_helper.api_helper import devide_date
''' '''



class get_predic_data(object):

    # _predicArea = str  ## 선택한 지역들(s).

    # ## 처음에 지역들 선택하고 날짜는 일별예측(30일), 월별예측1(past12개월), 월별예측2(coming24개월), 년별(5년) 동일.
    # ## 나주, 광주 등 각 지역마다 값을 처리할떄는 각 함수에 지역 이름 넣어서 처리. X
    # ## 최근 12개월은 시작 날짜가 -1년부터 시작 하기 때문에 일치하지가 않았다ㅠ
    # def __init__(self, start_year, start_month, start_day):
    #     self._start_year = start_year
    #     self._start_month = start_month
    #     self._start_day = start_day
    #     # self._predicTarget = predicTarget  ## 예측 대상(insu, sub)
    #     # self._predicArea = predicArea  ## 선택한 지역들(s).


    def get_Daily_coming_30days_vaule(self, predicArea, start_date):

        start_year, start_month, start_day = devide_date(start_date)
        # start_date = str(start_date)
        # start_year = int(start_date[0:4])
        # start_month = int(start_date[4:6])
        # start_day = int(start_date[6:8])

        path = folder_path + 'result/%s/predict_%s_%s_%s_%s_daily' % (start_date, predicArea, start_year, start_month, start_day)
        # file = '/home/uk/PredictionServer/prediction/result/predict_naju_2019_1_1_daily'
        print(path)
        if not os.path.isfile(path):
            return False

        with open(path, 'r') as short_t_save:
            result = short_t_save.read().replace("\n","").replace("[","").replace("]","")

        result = result.split(" ")

        final_result = list()
        for i in result:
            if i:
                final_result.append(float(i))

        final_result_date = list()
        syear, smonth, sday = devide_date(start_date)

        for a in range(30):
            # print(syear, smonth, sday )

            start_date_str = '%04d-%02d-%02d' % (syear, smonth, sday)
            final_result_date.append(start_date_str)


            if sday >= 28:
                if smonth == 1 or 3 or 5 or 7 or 8 or 10 or 12:
                    if sday == 31:
                        sday = 0
                        if smonth == 12:
                            smonth = 1
                            syear += 1
                        else:
                            smonth += 1

                elif smonth == 4 or 6 or 9 or 11:
                    if sday == 30:
                        sday = 0
                        smonth += 1

                elif smonth == 2:
                    if sday == 29:
                        sday = 0
                        smonth += 1

            sday += 1


        result_vv = []
        for i in range(30):
            kk = [final_result_date[i], final_result[i]]
            result_vv.append(kk)

        result_vv.insert(0, ["date","value"])
        # print(result_vv)
            # start_date = '%04d%02d%02d' % (syear, smonth, sday)
        # print(final_result)
        # print(final_result_date)
        # result = dict(zip(final_result_date, final_result))
        # print(result)

        return result_vv

    #####################################################################

    ## 최근 12개월 이기때문에 month_range = 12로 고정.

    ## set에서 실행 시킨후 get에서 value 얻으면 됨.

    def get_Monthly_latest_12months_daily_value(self, predicArea, start_year, start_month, temp_mode, sub_mode, start_date):
        path = folder_path+'result/%d/past_%s_%d_%d_%d_T%d_S%d_daily'%(start_date, predicArea, start_year, start_month, 12, temp_mode, sub_mode)
        # file = '/home/uk/PredictionServer/prediction/result/predict_naju_2019_1_1_daily'
        print(path)
        if not os.path.isfile(path):
            return False
        final_result = dict()

        pddata = pd.read_csv(path, delim_whitespace=True)
        import prediction.predict_common as predict_common

        category = predict_common.get_category(predicArea)

        data1 = "year month date"
        data2 = str()
        for tidx in range(len(category)):
            data2 += "%s_pred " % (category[tidx])

        # data2의 맨처음/마지막 공백제거
        data2 = data2.strip()
        # print("pddata: ",pddata)
        # print("dataname: ",data2)

        for index, row in sorted(pddata.iterrows()):
            datavalue1 = []
            # datavalue1_str = str()
            for i in data1.split(" "):
                datavalue1.append(row[i])

            datavalue1_str = '%04d-%02d-%02d' % (datavalue1[0],datavalue1[1],datavalue1[2])

            datavalue2 = []
            for i in data2.split(" "):
                datavalue2.append(row[i])
            # print(datavalue2)
            # temp_list = [date]

            M = dict(zip(data2.split(" "), datavalue2))
            L = {datavalue1_str:M}
            final_result.update(L)

            # print(final_result)

        return final_result


    def get_Monthly_latest_12months_monthly_value(self, predicArea, start_year, start_month, temp_mode, sub_mode,start_date):
        path = folder_path+'result/%d/past_%s_%d_%d_%d_T%d_S%d_monthly'%(start_date, predicArea, start_year, start_month, 12, temp_mode, sub_mode)
        # file = '/home/uk/PredictionServer/prediction/result/predict_naju_2019_1_1_daily'
        print(path)
        if not os.path.isfile(path):
            return False

        with open(path, 'r') as f:
            pddata2 = f.readline().strip()
            pddata2 = pddata2.split(" ")[2:]

        ## 파일로 값의 이름을 읽어서 찾아냄.
        print(pddata2)

        final_result = dict()
        value_list = []

        pddata = pd.read_csv(path, delim_whitespace=True)
        # print(short_term_data)
        # print("short_term_data: ",short_term_data)
        import prediction.predict_common as predict_common

        category = predict_common.get_category(predicArea)

        data1 = "year month"
        # data2 = str()
        # for tidx in range(len(category)):
        #     data2 += "%s_pred " % (category[tidx])

        # data2의 맨처음/마지막 공백제거
        # data2 = data2.strip()
        # print("pddata: ",pddata)
        # print("dataname: ",data2)

        for index, row in sorted(pddata.iterrows()):
            datavalue1 = []
            # datavalue1_str = str()
            for i in data1.split(" "):
                datavalue1.append(row[i])

            datavalue1_str = '%04d-%02d' % (datavalue1[0], datavalue1[1])

            datavalue2 = []
            for i in pddata2:

                datavalue2.append(row[i])
            # print(datavalue2)
            # temp_list = [date]

            datavalue2.insert(0, datavalue1_str)

            value_list.append(datavalue2)
            # M = dict(zip(pddata2, datavalue2))
            # L = {datavalue1_str: M}
            # final_result.update(L)
        pddata2.insert(0, "date")

            # print(final_result)
        # print(pddata2)
        # print('==================')
        # print(datavalue2)
        value_list.insert(0,pddata2)
        # print(datavalue1_str)
        # print(datavalue2)
        return value_list


    #####################################################################

    # 다가오는 24개월 이기 때문에 month_range=24 고정.

    ## set 실행 후, get으로 value 얻음.
    def get_Monthly_coming_24months_daily_value(self, predicArea, start_year, start_month,start_date):
        path = folder_path + 'result/%d/coming_%s_%d_%d_%d_daily' % (
        start_date, predicArea, start_year, start_month, 24)
        # file = '/home/uk/PredictionServer/prediction/result/predict_naju_2019_1_1_daily'
        print(path)
        if not os.path.isfile(path):
            return False
        final_result = dict()

        pddata = pd.read_csv(path, delim_whitespace=True)
        import prediction.prediction_ETRI.predict_common as predict_common

        category = predict_common.get_category(predicArea)

        data1 = "year month date"
        data2 = str()
        for tidx in range(len(category)):
            data2 += "%s_pred " % (category[tidx])

        # data2의 맨처음/마지막 공백제거
        data2 = data2.strip()
        # print("pddata: ",pddata)
        # print("dataname: ",data2)

        for index, row in sorted(pddata.iterrows()):
            datavalue1 = []
            # datavalue1_str = str()
            for i in data1.split(" "):
                datavalue1.append(row[i])

            datavalue1_str = '%04d-%02d-%02d' % (datavalue1[0], datavalue1[1], datavalue1[2])

            print(data2)
            ## 각 이름으로 값을 가져옴.
            ## house_pred houseCooking_pred houseJHeating_pred salesOne_pred salesTwo_pred bizHeating_pred bizCooling_pred industry_pred heatFacility_pred heatCombined_pred CNG_pred
            datavalue2 = []
            for i in data2.split(" "):
                datavalue2.append(row[i])
            # print(datavalue2)
            # temp_list = [date]

            M = dict(zip(data2.split(" "), datavalue2))
            L = {datavalue1_str: M}
            final_result.update(L)

            # print(final_result)

        return final_result

    def get_Monthly_coming_24months_monthly_value(self, predicArea, start_year, start_month,start_date):
        path = folder_path + 'result/%d/coming_%s_%d_%d_%d_monthly' % (
        start_date, predicArea, start_year, start_month, 24)
        # file = '/home/uk/PredictionServer/prediction/prediction_ETRI/result/predict_naju_2019_1_1_daily'
        print(path)
        if not os.path.isfile(path):
            return False

        with open(path, 'r') as f:
            pddata2 = f.readline().strip()
            pddata2 = pddata2.split(" ")[2:]

        final_result = dict()

        pddata = pd.read_csv(path, delim_whitespace=True)
        # print(short_term_data)
        # print("short_term_data: ",short_term_data)
        import prediction.prediction_ETRI.predict_common as predict_common

        category = predict_common.get_category(predicArea)

        data1 = "year month"
        # data2 = str()
        # for tidx in range(len(category)):
        #     data2 += "%s_pred " % (category[tidx])

        # data2의 맨처음/마지막 공백제거
        # data2 = data2.strip()
        # print("pddata: ",pddata)
        # print("dataname: ",data2)
        value_list = []
        for index, row in sorted(pddata.iterrows()):
            datavalue1 = []
            # datavalue1_str = str()
            for i in data1.split(" "):
                datavalue1.append(row[i])

            datavalue1_str = '%04d-%02d' % (datavalue1[0], datavalue1[1])

            datavalue2 = []
            for i in pddata2:
                datavalue2.append(row[i])
            # print(datavalue2)
            # temp_list = [date]

            datavalue2.insert(0, datavalue1_str)

            value_list.append(datavalue2)
            # M = dict(zip(pddata2, datavalue2))
            # L = {datavalue1_str: M}
            # final_result.update(L)
        pddata2.insert(0, "date")

        # print(final_result)
        # print(pddata2)
        # print('==================')
        # print(datavalue2)
        value_list.insert(0, pddata2)
        # print(datavalue1_str)
        # print(datavalue2)
        return value_list

    #####################################################################
    def get_Yearly_coming_5years_month(self, predicArea, start_year, start_date):
        path = folder_path + 'result/%d/yearly/coming_%s_%d_to_%d_monthly.csv' % (
            start_date, predicArea, start_year, start_year+5)
        # file = '/home/uk/PredictionServer/prediction/prediction_ETRI/result/predict_naju_2019_1_1_daily'
        print(path)
        if not os.path.isfile(path):
            return False

        with open(path, 'r') as f:
            pddata2 = f.readline().strip()
            pddata2 = pddata2.split(" ")[2:]

        final_result = dict()

        pddata = pd.read_csv(path, delim_whitespace=True)


        data1 = "year month"

        value_list = []
        for index, row in sorted(pddata.iterrows()):
            datavalue1 = []
            # datavalue1_str = str()
            for i in data1.split(" "):
                datavalue1.append(row[i])

            datavalue1_str = '%04d-%02d' % (datavalue1[0], datavalue1[1])

            datavalue2 = []
            for i in pddata2:
                datavalue2.append(row[i])
            # print(datavalue2)
            # temp_list = [date]

            datavalue2.insert(0, datavalue1_str)

            value_list.append(datavalue2)
            # M = dict(zip(pddata2, datavalue2))
            # L = {datavalue1_str: M}
            # final_result.update(L)
        pddata2.insert(0, "date")

        # print(final_result)
        # print(pddata2)
        # print('==================')
        # print(datavalue2)
        value_list.insert(0, pddata2)
        # print(datavalue1_str)
        # print(datavalue2)
        return value_list




    def get_Yearly_coming_5years_year(self, predicArea, start_year, start_date):
        path = folder_path + 'result/%d/yearly/coming_%s_%d_to_%d_yearly.csv' % (
            start_date, predicArea, start_year, start_year + 5)
        # file = '/home/uk/PredictionServer/prediction/prediction_ETRI/result/predict_naju_2019_1_1_daily'
        print(path)
        if not os.path.isfile(path):
            return False

        with open(path, 'r') as f:
            pddata2 = f.readline().strip()
            pddata2 = pddata2.split(" ")[1:]

        final_result = dict()

        pddata = pd.read_csv(path, delim_whitespace=True)

        data1 = "year"

        for index, row in sorted(pddata.iterrows()):
            datavalue1 = []
            for i in data1.split(" "):
                datavalue1.append(row[i])

            datavalue1_str = '%04d' % (datavalue1[0])

            datavalue2 = []
            for i in pddata2:
                datavalue2.append(row[i])
            # print(datavalue2)
            # temp_list = [date]

            M = dict(zip(pddata2, datavalue2))
            L = {datavalue1_str: M}
            final_result.update(L)

            print(final_result)

        return final_result



class get_train_model(object):

    def __init__(self, pkey):
        ## weather+gas
        # self._trainedModel = trainedModel
        ## [{'str':'lwm2m/imr-ami-002/22000/0/5700'}]
        ## 해당 주소로 lwm2m 값을 가져와서 모델링.

        self._pkey = pkey

    def get_lwm2m(self, arguments):
        value = lwm2m_set(arguments)
        return value

    def train_model(self, filename, period_start, period_end, period_start_time, period_end_time):
        # argument = self.get_lwm2m()


        # 모델을 돌리면 모델결과가 변수(result) or 파일로 저장.
        print(period_start, period_end, period_start_time, period_end_time)
        # 1. return 으로 나오면 변수화 해서 파일로 저장
        # 2. 모델 돌리는 부분에 파일저장 있으면 안해도 됨.
        # model_start_set(self._trainedModel, argument)


        model_create(filename, period_start, period_end, period_start_time, period_end_time, self._pkey)

        # # 파일 저장.
        # with open('file','r') as f:
        #     result = f.readlines()

    def train_model_result(self, filename):

        # 모델 결과 읽기.
        file_path = folder_path2 + 'result/%d/%s.csv' % (self._pkey, filename)
        # with open(file_path,'r') as f:
        #     result = f.read().splitlines()


        # file_data = pd.read_csv(file_path, delim_whitespace=True)
        # file_data = pd.read_csv(file_path, delimiter=',')


        # with open(file_path,'r') as f:
        #     # numbers = [[int(i) for i in line.split()] for line in f.readlines()]
        #     # print(numbers)
        #     file_value = f.read().splitlines()
        #     # print(file_value)
        #
        #     final_result = []
        #     k=0
        #     for i in file_value:
        #         if k==0:
        #             pass
        #         else:
        #             i = i.split(',')
        #             # file_value = file_value[k].split(',')
        #             M = dict(zip(['date', 'value'], i))
        #             final_result.append(M)
        #         k+=1

            # print('========================================')
            # print(final_result)
        final_result = list()

        short_term_data = pd.read_csv(file_path, delim_whitespace=False)
        # print(short_term_data)
        # print("short_term_data: ",short_term_data)
        for index, row in short_term_data.iterrows():
            # print(row)
            date = row['date']
            value = row['value']

            temp_list = [date, int(value)]

            M = dict(zip(['date', 'value'], temp_list))
            #             final_result.append(M)
            final_result.append(M)


        # print(final_result)

        return final_result



## set_data_clas
def lwm2m_set(argument):
    value = argument
    return value

def model_start_set(model,argument):
    return model, argument


## .csv 파일 만듬.
def model_create(filename, period_start, period_end, period_start_time, period_end_time, pkey):
    value = 'date, value\n'

    # print("period_start: ",period_start)
    syear, smonth, sday = devide_date(period_start)
    eyear, emonth, eday = devide_date(period_end)

    d0 = date(syear, smonth, sday)  # date 객체1
    d1 = date(eyear, emonth, eday)  # date 객체2
    delta =  d1-d0  # 빼기

    # print(period_start_time)
    # print(period_end_time)
    time_value1 = period_start_time.split(":")
    time_value2 = period_end_time.split(":")


    hour_value1 = int(time_value1[0])
    minute_value1 = int()
    second_value1 = int()
    # print("hour_value: ",hour_value1)
    try:
        if time_value1[1]:
            minute_value1 = int(time_value1[1])
    except:
        minute_value1 = 0
        second_value1 = 0
    else:
        try:
            if time_value1[2]:
                second_value1 = int(time_value1[2])
        except:
            second_value1 = 0

    hour_value2 = int(time_value2[0])
    minute_value2 = int()
    second_value2 = int()

    try:
        if time_value2[1]:
            minute_value2 = int(time_value2[1])
    except:
        minute_value2 = 0
        second_value2 = 0
    else:
        try:
            if time_value2[2]:
                second_value2 = int(time_value2[2])
        except:
            second_value2 = 0


    final_result = 'date,value\n'

    import datetime
    for i in range(delta.days+1):

        addhours = 0
        # 하루 24시간.
        for k in range(24):
            ran = random.randrange(1,256)
            mydelta = datetime.timedelta(hours=hour_value1 + addhours)
            mytime = datetime.datetime.min + mydelta  # datetime.datetime은 년/월/일까지 계산하게 돼서 24시가 넘는 h는 일(day)로 변환됩니다.
            hour, minute, second = mytime.hour, mytime.minute+minute_value1, mytime.second+second_value1
            # print("hour: ", hour)

            if eyear <= syear and emonth <= smonth and eday == sday and hour_value2 < hour:
                pass
            elif eyear <= syear and emonth <= smonth and eday == sday and hour_value2 == hour and minute_value2 < minute:
                pass
            elif eyear <= syear and emonth <= smonth and eday < sday :
                pass

            else:
                date_time = '%d-%02d-%02d %02d:%02d:%02d, %d\n' % (syear, smonth, sday, hour, minute, second, ran)
                final_result += date_time

            addhours += 1

            if hour >= 23:
                if sday >= 28:
                    if smonth == 1 or 3 or 5 or 7 or 8 or 10 or 12:
                        if sday == 31:
                            sday = 0
                            if smonth == 12:
                                smonth = 1
                                syear += 1
                            else:
                                smonth += 1

                    elif smonth == 4 or 6 or 9 or 11:
                        if sday == 30:
                            sday = 0
                            smonth += 1

                    elif smonth == 2:
                        if sday == 28:
                            sday = 0
                            smonth += 1

                sday += 1




        # if sday >= 28:
        #     if smonth == 1 or 3 or 5 or 7 or 8 or 10 or 12:
        #         if sday == 31:
        #             sday = 0
        #             if smonth == 12:
        #                 smonth = 1
        #                 syear += 1
        #             else:
        #                 smonth += 1
        #
        #     elif smonth == 4 or 6 or 9 or 11:
        #         if sday == 30:
        #             sday = 0
        #             smonth += 1
        #
        #     elif smonth == 2:
        #         if sday == 28:
        #             sday = 0
        #             smonth += 1
        #
        # sday += 1



    # print(final_result)
    if not os.path.isdir(folder_path2 + 'result/%d' % (pkey)):
        os.makedirs(folder_path2 + 'result/%d' % (pkey))
        pass

    print(folder_path2 + 'result/%d/%s.csv' % (pkey, filename))

    with open(folder_path2 + 'result/%d/%s.csv' % (pkey, filename), 'w') as f:
        f.write(str(final_result))





# model_create("aa",20190829,20190902)




aa = get_predic_data()
#
# print(aa.get_Daily_coming_30days_vaule('naju',20191001))
# print(aa.get_Daily_coming_30days_vaule('naju',2019,1,1))
# print(aa.get_Monthly_latest_12months_daily_value('naju',2018,10,0,0,20191001))
# print(aa.get_Monthly_latest_12months_monthly_value('naju',2018,10,0,0,20191001))
# print(aa.get_Monthly_coming_24months_daily_value('naju',2019,1))
# print(aa.get_Monthly_coming_24months_monthly_value('naju',2019,10,20191003))
print(aa.get_Yearly_coming_5years_month('naju',2019,20191003))