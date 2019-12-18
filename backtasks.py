# -*- coding: utf-8 -*-

import sys, os
import threading
from multiprocessing import current_process
from celery import Celery
from API.api_helper.user_directory import root_path


## 큐 처리.
from threading import Thread
from queue import Queue
import time

from celery.exceptions import SoftTimeLimitExceeded
from celery import task
from flask_sse import sse

celery = Celery('task', broker='pyamqp://uk:0000@localhost:5672')

task_acks_late = True
worker_prefetch_multiplier = 1


# CELERY_TASK_PROTOCOL = 5
CELERY_ENABLE_UTC= False

celery.conf.task_protocol = 5
worker_max_memory_per_child = 300000  # 3000MB
# broker_trainsport_options = {'visibility_timeout':18000}

filepath = root_path+'/detectkey/'
# CUDA_VISIBLE_DEVICES = ''
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', "project.settings.server")

# #워커가 초기화됬을때
# @worker_init.connect
# def init_worker(**kwargs):
# 	print('init')
#
# #워커가 종료됬을때
# @worker_shutdown.connect
# def shutdown_worker(**kwargs):
# 	print('shut')

################################################################################
# 큐
in_queue = Queue()

# thread = Thread(target=work).start()

def work(name):
    try:
        while 1:
            if in_queue.empty() == True:
                break
            else:
                time.sleep(1)
                print('work3while')
                print(in_queue.empty())
                pass
        print('work3')
        in_queue.put_nowait(name)   # 큐를 넣는다.
        ## 실행.
        in_queue.get_nowait() ## 큐 완료되면 뺴냄.

        print('work-done3')
    except:
        print('work3 pass')
        pass
################################################################################



@celery.task(name='daily', time_limit=100)
def daily(predicArea, start_year, start_month, start_day, date, user_key, detectkey):

    Thread = threading.Thread(target=daily_exe, args=(predicArea, start_year, start_month, start_day, date, user_key, detectkey))
    Thread.start()



def daily_exe(predicArea, start_year, start_month, start_day, date, user_key, detectkey):
    print(str(predicArea), int(start_year), int(start_month), int(start_day), int(date), user_key, detectkey)
    current_process()._config = {'semprefix': '/mp'}
    sys.path.insert(0, root_path)
    from prediction.predict_daily import main
    main(str(predicArea), int(start_year), int(start_month), int(start_day), int(date), user_key, detectkey)

    print('dddddddddddddddddddddddddddddddddddddddddddddddd')
    # message="daily_" + str(detectkey)
    #
    # if not os.path.isdir(filepath):
    #     os.mkdir(filepath)
    # with open(filepath+message,'w') as f:
    #     f.write(message)
    return True

################################################################################

@celery.task(name='monthly1')
def monthly1(predicArea, start_year, start_month, month_range, temp_mode, sub_mode, start_date, user_key, detectkey):
    Thread = threading.Thread(target=monthly1_exe, args=(predicArea, start_year, start_month, month_range, temp_mode, sub_mode, start_date, user_key, detectkey))
    Thread.start()

def monthly1_exe(predicArea, start_year, start_month, month_range, temp_mode, sub_mode, start_date, user_key, detectkey):
    current_process()._config = {'semprefix': '/mp'}
    sys.path.insert(0, root_path)
    from prediction.predict_past_12months import conduct_prediction
    conduct_prediction(predicArea, start_year, start_month, month_range, temp_mode, sub_mode, start_date, user_key, detectkey)
    # message = "monthly1_" + str(detectkey)
    # if not os.path.isdir(filepath):
    #     os.mkdir(filepath)
    # with open(filepath + message, 'w') as f:
    #     f.write(message)
    return True

################################################################################

@celery.task(name='monthly2')
def monthly2(predicArea, start_year, start_month, month_range, start_date, user_key, detectkey):
    Thread = threading.Thread(target=monthly2_exe, args=(predicArea, start_year, start_month, month_range, start_date, user_key, detectkey))
    Thread.start()

def monthly2_exe(predicArea, start_year, start_month, month_range, start_date, user_key, detectkey):
    current_process()._config = {'semprefix': '/mp'}
    sys.path.insert(0, root_path)
    from prediction.predict_coming_24months import conduct_prediction
    conduct_prediction(predicArea, start_year, start_month, month_range, start_date, user_key, detectkey)
    # message = "monthly2_" + str(detectkey)
    # if not os.path.isdir(filepath):
    #     os.mkdir(filepath)
    # with open(filepath + message, 'w') as f:
    #     f.write(message)
    return True

################################################################################

@celery.task(name='yearly')
def yearly(predicArea, start_year, date, user_key, detectkey):
    Thread = threading.Thread(target=yearly_exe, args=(predicArea, start_year, date, user_key, detectkey))
    Thread.start()

def yearly_exe(predicArea, start_year, date, user_key, detectkey):
    current_process()._config = {'semprefix': '/mp'}
    sys.path.insert(0, root_path)
    from prediction.predict_coming_5years import main
    main(predicArea, start_year, date, user_key, detectkey)
    # message = "yearly_" + str(detectkey)
    # if not os.path.isdir(filepath):
    #     os.mkdir(filepath)
    # with open(filepath + message, 'w') as f:
    #     f.write(message)
    return True

################################################################################