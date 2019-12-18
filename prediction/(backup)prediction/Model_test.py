# -*- coding: utf-8 -*-

# 스케줄 종류에는 여러가지가 있는데 대표적으로 BlockingScheduler, BackgroundScheduler 입니다
# BlockingScheduler 는 단일수행에, BackgroundScheduler은 다수 수행에 사용됩니다.
# 여기서는 BackgroundScheduler 를 사용하겠습니다.

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError


import time
import os
import requests
from bs4 import BeautifulSoup
from API.api_helper.api_helper import response_json_list,response_json_value
import json
from collections import OrderedDict

aaaaa = 0

# BackgroundScheduler 를 사용하면 stat를 먼저 하고 add_job 을 이용해 수행할 것을 등록해줍니다.
sched = BackgroundScheduler()
sched.start()



def job():
    time.sleep(20)
    print("I'm working...", "| [time] "
          , str(time.localtime().tm_hour) + ":"
          + str(time.localtime().tm_min) + ":"
          + str(time.localtime().tm_sec))

def job3():
    print("3-----------------")
    print("aaaaa: ",aaaaa)
    time.sleep(20)
    print("33333333333333333...", "| [time] "
          , str(time.localtime().tm_hour) + ":"
          + str(time.localtime().tm_min) + ":"
          + str(time.localtime().tm_sec))

def job_2():
    print("Job2 --------------------: ", "| [time] "
          , str(time.localtime().tm_hour) + ":"
          + str(time.localtime().tm_min) + ":"
          + str(time.localtime().tm_sec))
    print("aaaaa: ", aaaaa)

    if aaaaa == 1:
        sched.add_job(job3, 'cron', id="test_3")

        print("aaaaa: ", aaaaa)

    # global aaaaa
    # aaaaa = 1

    print("2222222222222222222")


##------------------------------------------------------------------------------------

data = ""
for tidx in range(30):
    if tidx < 3:
        data += "pred_short_day %d " % (tidx+1)
    elif 3 <= tidx and tidx < 11:
        data += "pred_mid_day %d " % (tidx+1)
    else:
        data += "pred_long %d " % (tidx+1)

# print(data)

from API.api_helper.user_directory import folder_prediction_path
tmp_for_pred = "rm -rf " + folder_prediction_path + "data/tmp_for_pred/*"
# print(tmp_for_pred)

script="cp -R"
scr_list = ["data/date", "data/insu", "data/sub", "data/temperature", "data/tmp_for_pred/"]
for teaa in scr_list:
    script += " " + teaa
os.system(script)
## "cp -R data/date data/insu data/sub data/temperature data/tmp_for_pred/"
## "cp -R data/date data/insu data/sub data/temperature data/tmp_for_pred/"

# print(script)
# # BackgroundScheduler 를 사용하면 stat를 먼저 하고 add_job 을 이용해 수행할 것을 등록해줍니다.
# sched = BackgroundScheduler()
# sched.start()
#
#
# # interval - 매 3조마다 실행
# sched.add_job(job, 'interval', seconds=30, id="test_2")
#
# # cron 사용 - 매 5초마다 job 실행
# # 	: id 는 고유 수행번호로 겹치면 수행되지 않습니다.
# # 	만약 겹치면 다음의 에러 발생 => 'Job identifier (test_1) conflicts with an existing job'
# sched.add_job(job_2, 'cron', second='*/5', id="test_1")
#
# # cron 으로 하는 경우는 다음과 같이 파라미터를 상황에 따라 여러개 넣어도 됩니다.
# # 	매시간 59분 10초에 실행한다는 의미.
# # sched.add_job(job_2, 'cron', minute="59", second='10', id="test_10")
#
#
# count = 0
# while True:
#     # print("Running main process...............")
#     time.sleep(1)

import pandas as pd
import os
from calendar import monthrange


def predict_temp(area, target_year, target_mon):
    '''
    This function estimates temperature of target_year.target_month by averaging the temperature of the same date of recent 4 years.
    Args:
        area: string, target area of prediction
        target_year: int, the target year of prediction
        target_mon: int, the target month of prediction
    Returns:
        prev_avg_temp: np.array, predicted daily temperature of target_year.target_mon
    '''

    # examine the existence of a target file to write prediction result. the prediction results will be used for further prediction.
    need_to_write = 0
    # - the target file does not exist
    if not os.path.isfile(folder_prediction_path + 'data/tmp_for_pred/temperature/%s_temp_%d' % (area, target_year)):
        tmp_f = open(folder_prediction_path + 'data/tmp_for_pred/temperature/%s_temp_%d' % (area, target_year), 'w')
        tmp_f.write("year month date avgTemp maxTemp minTemp\n")
        need_to_write = 1
    # - the target file exists
    else:
        temp_tmp = pd.read_csv(folder_prediction_path + 'data/tmp_for_pred/temperature/%s_temp_%d' % (area, target_year),
                               delim_whitespace=True)
        same_month = temp_tmp[temp_tmp['month'] == target_mon]

        # -- the prediction results of target_year.target_mon are already written.
        # -- note that this function can be called several times for multiple categoriesy for the same target_year.target_mon
        # -- just need to return the written results
        if len(same_month) > 0:
            return np.reshape(np.array(same_month['avgTemp']), (-1, 1))
        # -- need to conduct prediction
        else:
            need_to_write = 1
            tmp_f = open(folder_prediction_path + 'data/tmp_for_pred/temperature/%s_temp_%d' % (area, target_year), 'a')

    if need_to_write == 1:

        # load the temperature data of recent 4 years
        for tyear in range(target_year - 4, target_year):
            # read the temp data
            temp_data_tmp = pd.read_csv(folder_prediction_path + 'data/tmp_for_pred/temperature/%s_temp_%d' % (area, tyear),
                                        delim_whitespace=True)
            # merge the read data into one data for easy processing
            if tyear == target_year - 4:
                temp_data = temp_data_tmp
            else:
                temp_data = temp_data.append(temp_data_tmp)

        # get the number of days of target_year.target_month
        mon_days = monthrange(target_year, target_mon)[1]

        # for each day of target_year.target_month
        prev_avg_temp = []
        for tday in range(1, mon_days + 1):
            if target_mon == 2 and tday == 29:
                tday = 28
            prev_avg_temp_list = []

            # extract avgTemp from the data of recent 4 years
            for tyear in range(target_year - 4, target_year):
                prev_same_year = temp_data[temp_data['year'] == tyear]
                prev_same_month = prev_same_year[prev_same_year['month'] == target_mon]
                target_day = prev_same_month[prev_same_month['date'] == tday]

                avg_temp = target_day['avgTemp'].values[0]
                prev_avg_temp_list.append(avg_temp)

            # averaging 'avgTemp' of recent 4 years
            avg_over_years = np.mean(prev_avg_temp_list)
            prev_avg_temp.append([avg_over_years])

            tmp_f.write("%d %02d %02d %.2f %.2f %.2f\n" % (
            target_year, target_mon, tday, avg_over_years, avg_over_years, avg_over_years))

        tmp_f.close()

        # return predicted or true avgTemp
        return np.array(prev_avg_temp)

# import os
# import sys
# teata = '/home/lee/PredectionServer/prediction/prediction_ETRI/result/coming_naju_2019_1_24_daily'
#
# with open(teata,'w') as ff:
#     ff.readlines()


url = "http://192.168.0.139:19480/api/weather/58,74/mtf?startDate=20190923&startTime=0000&endDate=20190923&endTime=2400"
web_page = requests.get(url)
soup = BeautifulSoup(web_page.text, "html.parser")
# print(soup)

r = requests.get(url).text
json_data = pd.read_json(r)

temp_tmp = pd.read_csv(folder_prediction_path + 'data/tmp_for_pred/temperature/%s_temp_%d' % (area, target_year), delim_whitespace=True)
