# -*- coding: utf-8 -*-
# 날씨 정보 및 과거 데이터를 얻음.

'''general'''
import os
'''library'''
import requests
import pandas as pd
import json# 현재 예측 단기/중기 .csv 저장소 -> 'naju_mid_term_2019_10_03' 형식으로
'''directory'''
from API.api_helper.user_directory import folder_prediction_path
from API.api_helper.api_helper import response_json_list, response_json_value

# pd 리스트 모두 출력.
pd.set_option('display.max_row',None)
pd.set_option('display.max_columns',None)


## ETRI prediction_csv 파일 데이터 get.
class set_predic_data(object):

    # _predicArea = str  ## 선택한 지역들(s).

    # def __init__(self):
    #     return
    #     # self._predicTarget = predicTarget  ## 예측 대상(insu, sub)
    #     self._predicArea = predicArea  ## 예측 지역들(s).


    ## 블러올 때, class 한번 선언후 각 함수(지역,값,값) 형태로
    def set_Daily_coming_30days(self, predicArea, start_year, start_month, start_day, user_key, detectkey):
        # set_Daily_coming_30day_short_trem_save, set_Daily_coming_30day_mid_trem_save 로 단기3일, 중기 8일 예측 저장하고
        # set_Daily_coming_30day 함수로 모델링 하는거 까지. (결과 불러오는 거는 중간에 계속 불러올 수 있으니 따로 함수)
        # print(predicArea)
        # print(start_year)
        # print(start_month)
        # print(start_day)
        # print(user_key)
        # print(detectkey)

        ## todo: 유민씨 API 받아오는 곳 아침 7시를 기준으로 그날 7시가 안되면 전날짜로 요청, 7시 넘으면 해당 날짜로.
        ## TODO: 수정해야함. start_day(20191007) 받으면 11일기록 받는 함수로 유민씨 API---------------------------
        '''
        1. 11일 예측 데이터 받아옴.
        2. short(3) / mid(8) 나눠서 forecast/ 에 저장.
        3. 모델 실행.

        '''
        # start_day=20191004
        date = '%d%02d%02d' % (start_year, start_month, start_day)


        # 데이터 불러옴.
        weather = set_weather_data(predicArea)
        json_data = weather.set_predict_short_mid_term(date)



        # print("json_data", json_data)
        # 데이터 저장.
        ## 받아온 json 값에서 short/mid로 나눈다.

        short_mid_folder = folder_prediction_path + 'data/forecast/%s/' % (date)
        # print("shomid_folder: ",short_mid_folder)

        result_value = dict()
        max_dict= dict()
        min_dict= dict()
        avg_dict= dict()
        min = []
        max = []
        avg = []
        for i in range(11):

            maxkey = 'taMax%d' % (i)
            minkey = 'taMin%d' % (i)
            avgv = (json_data.get(maxkey) + json_data.get(minkey)) / 2.0
            # print("max: ", json_data.get(maxkey))
            # print("min: ", json_data.get(minkey))
            # print("avg: ", avgv)

            max.append(json_data.get(maxkey))
            min.append(json_data.get(minkey))
            avg.append(avgv)

            max_dict['maxTemp'] = max
            min_dict['minTemp'] = min
            avg_dict['avgTemp'] = avg

            result_value.update(max_dict)
            result_value.update(min_dict)
            result_value.update(avg_dict)

            if i == 2:
                short_value = pd.DataFrame(result_value)
                # print(short_value)
                if not os.path.isdir(short_mid_folder):
                    os.makedirs(short_mid_folder)
                with open(folder_prediction_path + 'data/forecast/%s/%s_short_term' % (date, predicArea), 'w') as s:
                    s.write(str(short_value))
                result_value = dict()
                max_dict = dict()
                min_dict = dict()
                avg_dict = dict()
                min = []
                max = []
                avg = []


        mid_value = pd.DataFrame(result_value)
        # print(mid_value)

        if not os.path.isdir(short_mid_folder):
            os.makedirs(short_mid_folder)
        with open(folder_prediction_path + 'data/forecast/%s/%s_mid_term' % (date, predicArea), 'w') as s:
            s.write(str(mid_value))
        # ## todo : Date로 저장한곳 찾아서 실행.
        #
        # ## /data/weather, insu, sub에 오늘보다 이전 데이터가 있어야함.
        # print("start backtask of api")
        from backtasks import daily, work
        # daily.apply_async((predicArea, start_year, start_month, start_day, date, user_key, detectkey), queue='lopri', countdown=10)
        ## lopri라는 큐에 task를 전송하고 10초 후 실행.
        daily.delay(predicArea, start_year, start_month, start_day, date, user_key, detectkey)
        # work(predicArea, start_year, start_month, start_day, date, user_key, detectkey)

        # from prediction.prediction_ETRI.predict_daily import main
        # main(predicArea, start_year, start_month, start_day, date)

        return

    ## short term save
    def set_Daily_coming_30day_short_trem_save(self, predicArea, date):
        # 해당 날짜 or 시간을 기입해 파일생성. 하루 이기 떄문에 시간은 0000, 2400 고정
        short_term_path = folder_prediction_path + 'data/forecast/%s/%s_short_term' % (date, predicArea)
        print("short_path: ", short_term_path)
        get_weather = set_weather_data(predicArea)
        get_list = ["t3h","tmn","tmx"]
        # save_value = get_weather.set_predict_short_term_filter('20190924', '0000', '20190924', '1000', get_list)
        save_value = get_weather.set_predict_short_mid_term()

        with open(short_term_path, 'w') as short_t_save:
            short_t_save.write(str(save_value))

        return

    ## mid_term save
    def set_Daily_coming_30day_mid_trem_save(self, predicArea, date):
        mid_term_path = folder_prediction_path + 'data/forecast/%s/%s_mid_term' % (date, predicArea)
        print("mid_path: ",mid_term_path)
        get_weather = set_weather_data(predicArea)
        get_list = ["maxTemp","minTemp","avgTemp"]

        save_value = get_weather.set_predict_short_mid_term()

        with open(mid_term_path, 'w') as mid_t_save:
            mid_t_save.write(str(save_value))

        return

    def set_Monthly_latest_12months(self, predicArea, start_year, start_month, month_range, temp_mode, sub_mode, start_date, user_key, detectkey):
        ## -4년 부터 계산 -> /data/temperature/naju가 현재 2014~2018년 까지 없음 그래서 2018년을 시작날짜로 잡아야 test 가능.
        ## 무조건 현재에서 1년 뒤꺼 가져와야함 최근 12개월 이니까.
        # main(area,오늘년도,오늘월(원하는 월),12(고정),1(옵션),1(옵션))

        # from prediction.prediction_ETRI.predict_past_12months import conduct_prediction
        # conduct_prediction(predicArea,start_year, start_month, month_range, temp_mode, sub_mode, start_date)

        from backtasks import monthly1
        monthly1.delay(predicArea, start_year, start_month, month_range, temp_mode, sub_mode, start_date, user_key, detectkey)
        return

    def set_Monthly_coming_24months(self, predicArea, start_year, start_month, month_range, start_date, user_key, detectkey):
        # from prediction.prediction_ETRI.predict_coming_24months import conduct_prediction
        # conduct_prediction(predicArea, start_year, start_month, month_range, start_date)
        # 과거 -3년 있어야
        from backtasks import monthly2
        monthly2.delay(predicArea, start_year, start_month, month_range, start_date, user_key, detectkey)

        return

    def set_Yearly_coming_5years(self, predicArea, start_year, date, user_key, detectkey):
        # from prediction.prediction_ETRI.predict_coming_5years import main
        # main(predicArea,start_year, date)

        from backtasks import yearly
        yearly.delay(predicArea, start_year, date, user_key, detectkey)

        return

    # def get_temp_min_max_avg(self, json_data, i):
    #
    #     maxkey = 'taMax%d' % (i)
    #     minkey = 'taMin%d' % (i)
    #     maxv = json_data.get(maxkey)
    #     minv = json_data.get(minkey)
    #     avgv = (maxv + minv) / 2.0
    #     print("max: ", json_data.get(maxkey))
    #     print("min: ", json_data.get(minkey))
    #     print("avg: ", avgv)
    #
    #     return maxv, minv, avgv


## 날씨 서버에서 <과거> 측정데이터 get. [종관]
## https://docs.google.com/spreadsheets/d/1QO1-BghvuAErtp8yG6OvkBAaioqXjwb_xgtUY8cPcf0/edit#gid=2054223190
class set_weather_data(object):

    def __init__(self, area):
        #TODO: 단기:격자, 나머지:지역(코드가 중기,종간 마다 다름.)
        if area == 'naju':
            self._area_grid = '58,74' # 격자
            self._area_code = '156' # 지역 (stnId)
        elif area == 'gwanju':
            self._area_grid = '58,74'  # 격자
            self._area_code = '156'  # 지역 (stnId)
        else:
            self._area_grid = '58,74'  # 격자
            self._area_code = '156'  # 지역 (stnId)

        # self._startDate = startDate  ## 시작일
        # self._endDate = endDate  ## 종료일
        # self._startTime = startTime  ## 시작 시간
        # self._endTime = endTime  # 종료 시간

    #filter
    #http://192.168.0.139:19480/api/weather/156/amWeather/day?startDate=20190701&startTime=0000&endDate=20190701&endTime=0200&filter=maxTemp,minTemp,avgTemp

    ## 과거측정데이터 - 시간별 측정 데이터.
    ## http://192.168.0.139:19480/api/weather/58,74/amWeather/hour?startDate=20190901&startTime=0000&endDate=20190901&endTime=0200
    def set_past_data_by_time(self, startDate, startTime, endDate, endTime):
        query = 'http://192.168.0.139:19480/api/weather/%s/amWeather/hour?startDate=%s&startTime=%s&endDate=%s&endTime=%s' % (
        self._area_code, startDate, startTime, endDate, endTime)
        ## ex) query='http://192.168.0.139:19480/api/weather/58,74/amWeather/hour?startDate=20190901&startTime=0000&endDate=20190901&endTime=0200'
        r = requests.get(query).text
        json_data = pd.read_json(r)
        # print(json_data)
        return json_data

    ## &filter=maxTemp,minTemp,avgTemp
    def set_past_data_by_time_filter(self, startDate, startTime, endDate, endTime, filter):
        query = 'http://192.168.0.139:19480/api/weather/%s/amWeather/hour?startDate=%s&startTime=%s&endDate=%s&endTime=%s' % (
        self._area_code, startDate, startTime, endDate, endTime)
        query = self.set_filter_helper(query,filter)
        r = requests.get(query).text
        json_data = pd.read_json(r)
        # print(json_data)
        return json_data

    ## 과거측정데이터 - 일별 측정 데이터(그날 평균)
    ## http://192.168.0.139:19480/api/weather/156/amWeather/day?startDate=20190901&startTime=0000&endDate=20190901&endTime=2300
    def set_past_data_by_day(self, startDate, startTime, endDate, endTime):
        query = 'http://192.168.0.139:19480/api/weather/%s/amWeather/day?startDate=%s&startTime=%s&endDate=%s&endTime=%s' % (
        self._area_code, startDate, startTime, endDate, endTime)
        r = requests.get(query).text
        json_data = pd.read_json(r)
        # print(json_data)
        return json_data

    def set_past_data_by_day_filter(self, startDate, startTime, endDate, endTime, filter):
        query = 'http://192.168.0.139:19480/api/weather/%s/amWeather/day?startDate=%s&startTime=%s&endDate=%s&endTime=%s' % (
        self._area_code, startDate, startTime, endDate, endTime)
        query = self.set_filter_helper(query,filter)

        r = requests.get(query).text
        json_data = pd.read_json(r)
        # print(json_data)
        return json_data

    ## prediction_data
    ## 날씨 [단기] get
    # http://192.168.0.139:19480/api/weather/58,74/stf?startDate=20190924&startTime=0800&endDate=20190924&endTime=1000
    def set_predict_short_term(self, startDate, startTime, endDate, endTime):
        ## 'http://192.168.0.139:19480/api/weather/58,74/stf?startDate=20190924&startTime=0800&endDate=20190924&endTime=1000'
        query = 'http://192.168.0.139:19480/api/weather/%s/stf?startDate=%s&startTime=%s&endDate=%s&endTime=%s' % (
        self._area_grid, startDate, startTime, endDate, endTime)
        r = requests.get(query).text
        json_data = pd.read_json(r)
        # print(json_data)
        return json_data

    # 값 얻는 부분.
    def set_predict_short_term_filter(self, startDate, startTime, endDate, endTime, filter):
        query = 'http://192.168.0.139:19480/api/weather/%s/stf?startDate=%s&startTime=%s&endDate=%s&endTime=%s' % (
        self._area_grid, startDate, startTime, endDate, endTime)
        # print(query)
        query = self.set_filter_helper(query,filter)
        r = requests.get(query).text

        json_data = pd.read_json(r)
        # print(json_data)
        return json_data

    ## prediction_data
    ## 날씨 [중기] get
    # http://192.168.0.139:19480/api/weather/58,74/mtf?startDate=20190923&startTime=0600&endDate=20190923&endTime=0700
    def set_predict_mid_term(self, startDate, startTime, endDate, endTime):
        query = 'http://192.168.0.139:19480/api/weather/%s/mtf?startDate=%s&startTime=%s&endDate=%s&endTime=%s' % (
        self._area_grid, startDate, startTime, endDate, endTime)
        r = requests.get(query).text
        json_data = pd.read_json(r)
        # print(json_data)
        return json_data

    def set_predict_mid_term_filter(self, startDate, startTime, endDate, endTime, filter):
        query = 'http://192.168.0.139:19480/api/weather/%s/mtf?startDate=%s&startTime=%s&endDate=%s&endTime=%s' % (
        self._area_grid, startDate, startTime, endDate, endTime)
        query = self.set_filter_helper(query,filter)
        r = requests.get(query).text
        json_data = pd.read_json(r)
        # print(json_data)
        return json_data



    # TODO: 유민씨 API 받아오는 부분 새로운 버전.
    # 값 얻는 부분.
    def set_predict_short_mid_term(self, date):

        start_date = str(date)
        start_year = int(start_date[0:4])
        start_month = int(start_date[4:6])
        start_day = int(start_date[6:8])

        Date = '%d.%d.%d' % (start_year, start_month, start_day)

        try:

            # http://192.168.0.139:19480/api/weather/58,74/autoenergy?baseDate=2019.10.07
            query = 'http://192.168.0.139:19480/api/weather/%s/autoenergy?baseDate=%s' % (
                self._area_grid, Date)
            r = requests.get(query).json()
        except Exception as e:
            print(e)
            print("weather_error")


        # print(r)
        # r = '[%s]' % (r)
        # json_data = pd.read_json(r)
        return r


    def set_filter_helper(self, query, filter):
        query += '&filter='
        for list_value in filter:
            if filter[-1] == list_value:
                query += '%s' % (list_value)
            else:
                query += '%s,' % (list_value)

        return query




## 해양
# aa = set_predic_data()
# aa.set_Daily_coming_30days('naju',2019,10,7)
# aa.set_Daily_coming_30day_short_trem_save('naju',20191004,20191004)
# aa.Monthly_latest_12months('naju',2018,1,1,1,1)
# aa.set_Monthly_coming_24months('naju',2019,1,24)
# aa.set_Daily_coming_30day_short_trem_save('naju','20191004','20191004')
# aa.set_Daily_coming_30day_mid_trem_save('naju','20191006','20191006')


# # ## 스마트E
# aa = set_weather_data('naju')
# print(aa.set_predict_short_mid_term(20191112))
# filter=["maxTemp","minTemp","avgTemp"]
# aa.past_data_by_time('20190901', '0000', '20190901', '0200')
# aa.past_data_by_time_filter('20190901', '0000', '20190901', '0200', filter)
# aa.past_data_by_day('20190901', '0000', '20190901', '0200')
# aa.past_data_by_day_filter('20190901', '0000', '20190901', '0200', filter)
# aa.predict_short_term('20190924', '0000', '20190924', '1000')
# aa.set_predict_mid_term('20190924', '0000', '20190924', '1000')


