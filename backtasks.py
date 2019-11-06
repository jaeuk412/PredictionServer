# -*- coding: utf-8 -*-

import sys, os
import threading
from multiprocessing import current_process
from celery import Celery
from API.api_helper.user_directory import root_path
from celery import task

celery = Celery('task', broker='pyamqp://uk:0000@localhost:5672')

CELERY_TASK_PROTOCOL = 1
celery.conf.task_protocol = 1
worker_max_memory_per_child = 3000000  # 3000MB
broker_trainsport_options = {'visibility_timeout':18000}
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

@celery.task(name='daily')
def daily(predicArea, start_year, start_month, start_day, date):
    Thread = threading.Thread(target=daily_exe, args=(predicArea, start_year, start_month, start_day, date))
    Thread.start()

def daily_exe(predicArea, start_year, start_month, start_day, date):
    current_process()._config = {'semprefix': '/mp'}
    sys.path.insert(0, root_path)
    from prediction.prediction_ETRI.predict_daily import main
    main(str(predicArea), int(start_year), int(start_month), int(start_day), int(date))
    return True

################################################################################

@celery.task(name='monthly1')
def monthly1(predicArea,start_year, start_month, month_range, temp_mode, sub_mode, start_date):
    Thread = threading.Thread(target=monthly1_exe, args=(predicArea,start_year, start_month, month_range, temp_mode, sub_mode, start_date))
    Thread.start()

def monthly1_exe(predicArea,start_year, start_month, month_range, temp_mode, sub_mode, start_date):
    current_process()._config = {'semprefix': '/mp'}
    sys.path.insert(0, root_path)
    from prediction.prediction_ETRI.predict_past_12months import conduct_prediction
    conduct_prediction(predicArea,start_year, start_month, month_range, temp_mode, sub_mode, start_date)
    return True

################################################################################

@celery.task(name='monthly2')
def monthly2(predicArea, start_year, start_month, month_range, start_date):
    Thread = threading.Thread(target=monthly2_exe, args=(predicArea, start_year, start_month, month_range, start_date))
    Thread.start()

def monthly2_exe(predicArea, start_year, start_month, month_range, start_date):
    current_process()._config = {'semprefix': '/mp'}
    sys.path.insert(0, root_path)
    from prediction.prediction_ETRI.predict_coming_24months import conduct_prediction
    conduct_prediction(predicArea, start_year, start_month, month_range, start_date)
    return True

################################################################################

@celery.task(name='yearly')
def yearly(predicArea,start_year, date):
    Thread = threading.Thread(target=yearly_exe, args=(predicArea,start_year, date))
    Thread.start()

def yearly_exe(predicArea,start_year, date):
    current_process()._config = {'semprefix': '/mp'}
    sys.path.insert(0, root_path)
    from prediction.prediction_ETRI.predict_coming_5years import main
    main(predicArea,start_year, date)
    return True

################################################################################