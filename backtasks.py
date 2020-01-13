# -*- coding: utf-8 -*-

import sys, os
import threading
import datetime
from multiprocessing import current_process
from celery import Celery
from API.api_helper.user_directory import root_path, folder_detectkey_path
from DB.DataBase.models import ResultTable
from DB.DataBase.database import db_session



## 큐 처리.
from threading import Thread
from queue import Queue
import time

from celery.exceptions import SoftTimeLimitExceeded
from celery import task
from flask_sse import sse

celery = Celery('task', broker='pyamqp://uk:0000@localhost:5672')

# task_acks_late = True
# worker_prefetch_multiplier = 1

# CELERYD_PREFETCH_MULTIPLIER = 0
# CELERY_TASK_PROTOCOL = 5
CELERY_ENABLE_UTC= False

celery.conf.task_protocol = 5
worker_max_memory_per_child = 3000  # 3000MB
# broker_trainsport_options = {'visibility_timeout':18000}

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
## todo: 파일로 Ing_detectkey 만들어서 실행 시키고 종료될때 Ing 없애기.
### While문 돌려서 파일에 Ing가 있으면 실행 X 방식으로 1개씩 실행.


###############################################################################


@celery.task(name='predict')
def predict(predicArea, start_year, start_month, start_day, month_range, temp_mode, sub_mode, start_date, user_key, detectkey, mode):
    ING_message = "ING_"+str(detectkey)
    # message = str(detectkey)

    if not os.path.isdir(folder_detectkey_path):
        os.mkdir(folder_detectkey_path)

    print('celery_task')

    w_break = 0
    while 1:
        if w_break == 1:
            break

        files = os.listdir(folder_detectkey_path)
        print(files)

        if not files:
            w_break = 1
        else:
            if any('ING' in s for s in files):
                print(mode)
                time.sleep(1)
                pass

            else:
                print('w_break = 1')
                w_break = 1
            time.sleep(1)

    value = db_session.query(ResultTable).get(detectkey)
    value.inserted = datetime.datetime.now()
    db_session.commit()


    print('make_ING_file')
    with open(folder_detectkey_path + ING_message, 'w') as f:
        f.write(str(detectkey))

    if mode == 1:
        Thread = threading.Thread(target=daily_exe, args=(
        predicArea, start_year, start_month, start_day, start_date, user_key, detectkey))
        Thread.start()
    elif mode == 2:
        Thread = threading.Thread(target=monthly1_exe, args=(predicArea, start_year, start_month, month_range, temp_mode, sub_mode, start_date, user_key, detectkey))
        Thread.start()
    elif mode == 3:
        Thread = threading.Thread(target=monthly2_exe, args=(predicArea, start_year, start_month, month_range, start_date, user_key, detectkey))
        Thread.start()
    elif mode == 4:
        Thread = threading.Thread(target=yearly_exe, args=(predicArea, start_year, start_date, user_key, detectkey))
        Thread.start()


@celery.task(name='daily')
def daily(predicArea, start_year, start_month, start_day, date, user_key, detectkey):
    print("---------------------------")
    print(predicArea, start_year, start_month, start_day, date, user_key, detectkey)
    ING_message = "ING_"+str(detectkey)
    # message = str(detectkey)

    if not os.path.isdir(folder_detectkey_path):
        os.mkdir(folder_detectkey_path)

    print('celery_task')

    w_break = 0
    while 1:
        if w_break == 1:
            break

        files = os.listdir(folder_detectkey_path)
        print(files)

        if not files:
            w_break = 1
        else:
            if any('ING' in s for s in files):
                print('daily_ING')
                time.sleep(1)
                pass

            else:
                print('w_break = 1')
                w_break = 1
            time.sleep(1)

    value = db_session.query(ResultTable).get(detectkey)
    value.inserted = datetime.datetime.now()
    db_session.commit()


    print('make_ING_file')
    with open(folder_detectkey_path + ING_message, 'w') as f:
        f.write(str(detectkey))

    Thread = threading.Thread(target=daily_exe, args=(predicArea, start_year, start_month, start_day, date, user_key, detectkey))
    Thread.start()

def daily_exe(predicArea, start_year, start_month, start_day, date, user_key, detectkey):
    # print(str(predicArea), int(start_year), int(start_month), int(start_day), int(date), user_key, detectkey)
    print('daily_exe')
    current_process()._config = {'semprefix': '/mp'}
    sys.path.insert(0, root_path)
    from prediction.predict_daily import main
    print(predicArea, start_year, start_month, start_day, date, user_key, detectkey)
    main(str(predicArea), int(start_year), int(start_month), int(start_day), int(date), user_key, detectkey)

    ING_message = "ING_" + str(detectkey)

    files = os.listdir(folder_detectkey_path)

    print(files)
    for i in files:
        if ING_message in i:
            print('edit_ingfile')
            # os.remove(folder_detectkey_path + i)
            new_name = ING_message.replace('ING_', 'DONE_')
            try:
                os.rename(folder_detectkey_path+ING_message, folder_detectkey_path+new_name)
            except:
                pass

    return

################################################################################

@celery.task(name='monthly1')
def monthly1(predicArea, start_year, start_month, month_range, temp_mode, sub_mode, start_date, user_key, detectkey):
    print("---------------------------")
    print(predicArea, start_year, start_month, month_range, temp_mode, sub_mode, start_date, user_key, detectkey)
    print('---------------------------monthly1----------------------------')
    print("detectkey: ", detectkey)
    ING_message = "ING_" + str(detectkey)
    if not os.path.isdir(folder_detectkey_path):
        os.mkdir(folder_detectkey_path)

    print('celery_task')

    w_break = 0
    while 1:
        if w_break == 1:
            break

        files = os.listdir(folder_detectkey_path)
        print(files)

        if not files:
            w_break = 1
        else:
            if any('ING' in s for s in files):
                print('monthly1_ING')
                time.sleep(1)
                pass

            else:
                print('w_break = 1')
                w_break = 1
            time.sleep(1)

    value = db_session.query(ResultTable).get(detectkey)
    value.inserted = datetime.datetime.now()
    db_session.commit()

    print('make_ING_file')
    with open(folder_detectkey_path + ING_message, 'w') as f:
        f.write(str(detectkey))

    Thread = threading.Thread(target=monthly1_exe, args=(predicArea, start_year, start_month, month_range, temp_mode, sub_mode, start_date, user_key, detectkey))
    Thread.start()

def monthly1_exe(predicArea, start_year, start_month, month_range, temp_mode, sub_mode, start_date, user_key, detectkey):
    current_process()._config = {'semprefix': '/mp'}
    sys.path.insert(0, root_path)
    from prediction.predict_past_12months import conduct_prediction
    conduct_prediction(predicArea, start_year, start_month, month_range, temp_mode, sub_mode, start_date, user_key, detectkey)

    ING_message = "ING_" + str(detectkey)

    files = os.listdir(folder_detectkey_path)

    print(files)
    for i in files:
        if ING_message in i:
            print('edit_ingfile')
            # os.remove(folder_detectkey_path + i)
            new_name = ING_message.replace('ING_', 'DONE_')
            try:
                os.rename(folder_detectkey_path + ING_message, folder_detectkey_path + new_name)
            except:
                pass

    return

################################################################################

@celery.task(name='monthly2')
def monthly2(predicArea, start_year, start_month, month_range, start_date, user_key, detectkey):
    print('---------------------------monthly2----------------------------')
    print(predicArea, start_year, start_month, month_range, start_date, user_key, detectkey)
    ING_message = "ING_" + str(detectkey)
    if not os.path.isdir(folder_detectkey_path):
        os.mkdir(folder_detectkey_path)

    print('celery_task')

    w_break = 0
    while 1:
        if w_break == 1:
            break

        files = os.listdir(folder_detectkey_path)
        print(files)

        if not files:
            w_break = 1
        else:
            if any('ING' in s for s in files):
                print('monthly2_ING')
                time.sleep(1)
                pass

            else:
                print('w_break = 1')
                w_break = 1
            time.sleep(1)

    value = db_session.query(ResultTable).get(detectkey)
    value.inserted = datetime.datetime.now()
    db_session.commit()

    print('make_ING_file')
    with open(folder_detectkey_path + ING_message, 'w') as f:
        f.write(str(detectkey))

    Thread = threading.Thread(target=monthly2_exe, args=(predicArea, start_year, start_month, month_range, start_date, user_key, detectkey))
    Thread.start()

def monthly2_exe(predicArea, start_year, start_month, month_range, start_date, user_key, detectkey):
    current_process()._config = {'semprefix': '/mp'}
    sys.path.insert(0, root_path)
    from prediction.predict_coming_24months import conduct_prediction
    conduct_prediction(predicArea, start_year, start_month, month_range, start_date, user_key, detectkey)

    ING_message = "ING_" + str(detectkey)

    files = os.listdir(folder_detectkey_path)

    print(files)
    for i in files:
        if ING_message in i:
            print('edit_ingfile')
            # os.remove(folder_detectkey_path + i)
            new_name = ING_message.replace('ING_', 'DONE_')
            try:
                os.rename(folder_detectkey_path + ING_message, folder_detectkey_path + new_name)
            except:
                pass

    return

################################################################################

@celery.task(name='yearly')
def yearly(predicArea, start_year, date, user_key, detectkey):
    print('---------------------------yearly----------------------------')
    print(predicArea, start_year, date, user_key, detectkey)
    ING_message = "ING_" + str(detectkey)
    if not os.path.isdir(folder_detectkey_path):
        os.mkdir(folder_detectkey_path)

    print('celery_task')

    w_break = 0
    while 1:
        if w_break == 1:
            break

        files = os.listdir(folder_detectkey_path)
        print(files)

        if not files:
            w_break = 1
        else:
            if any('ING' in s for s in files):
                print('yearly_ING')
                time.sleep(1)
                pass

            else:
                print('w_break = 1')
                w_break = 1
            time.sleep(1)

    value = db_session.query(ResultTable).get(detectkey)
    value.inserted = datetime.datetime.now()
    db_session.commit()

    print('make_ING_file')
    with open(folder_detectkey_path + ING_message, 'w') as f:
        f.write(str(detectkey))

    Thread = threading.Thread(target=yearly_exe, args=(predicArea, start_year, date, user_key, detectkey))
    Thread.start()

def yearly_exe(predicArea, start_year, date, user_key, detectkey):
    current_process()._config = {'semprefix': '/mp'}
    sys.path.insert(0, root_path)
    from prediction.predict_coming_5years import main
    main(predicArea, start_year, date, user_key, detectkey)

    ING_message = "ING_" + str(detectkey)

    files = os.listdir(folder_detectkey_path)

    print(files)
    for i in files:
        if ING_message in i:
            print('edit_ingfile')
            # os.remove(folder_detectkey_path + i)
            new_name = ING_message.replace('ING_', 'DONE_')
            try:
                os.rename(folder_detectkey_path + ING_message, folder_detectkey_path + new_name)
            except:
                pass

    return

################################################################################