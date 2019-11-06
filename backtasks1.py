import sys, os
import threading
from celery import Celery
import gc
#import tensorflow as tf
from celery.signals import worker_init, worker_shutdown


# celery = Celery('task', broker='pyamqp://uk:0000@localhost:5672/doky_host')
celery = Celery('task', broker='pyamqp://uk:0000@localhost:5672')

# worker_max_memory_per_child = 3000000  # 3000MB
# broker_trainsport_options = {'visibility_timeout':18000}
# CUDA_VISIBLE_DEVICES = ''


#워커가 초기화됬을때
@worker_init.connect
def init_worker(**kwargs):
	print('init')

#워커가 종료됬을때
@worker_shutdown.connect
def shutdown_worker(**kwargs):
	print('shut')
################################################################################

@celery.task(name='task')
def daily(predicArea, start_year, start_month, start_day, date):
    print("celery")
    Thread = threading.Thread(target=daily_exe, args=(predicArea, start_year, start_month, start_day, date))
    Thread.start()


def daily_exe(predicArea, start_year, start_month, start_day, date):
    print("celery_exe")
    print("=============================================")
    print("=============================================")
    from prediction.prediction_ETRI.predict_daily import main
    main(str(predicArea), int(start_year), int(start_month), int(start_day), int(date))
    return 0

################################################################################


@celery.task(name='psycho_2_7.backtasks.thread_prepro')
def thread_prepro(dpath, cpath, dataNum2):
    Thread = threading.Thread(target=preprocessing, args=(dpath, cpath, dataNum2))
    # Thread = threading.Thread(target=preprocessing, args=())
    Thread.start()

# max_calls_per_worker=1

# @cached_property
@celery.task(name='psycho_2_7.backtasks.thread_training')
def thread_training(dataid,modelid,tname,epochs, batch):
    # Thread = threading.Thread(target=training, args=(dataid,modelid,tname,epochs, batch))
    # Thread.start()
    return 0


@celery.task(name='psycho_2_7.backtasks.thread_tests')
def thread_tests(dataid,modelid,testid,trainname):
    Thread = threading.Thread(target=tests, args=(dataid,modelid,testid,trainname))
    Thread.start()


# Original functions ==================================================================================================
def preprocessing(dpath, cpath, dataNum2):
    # sys.path.insert(0, '/home/imr-ai/psycho_2_7/ProjectEn/backend_test')
    # from preprocess_MFCC import preprocessing

    # preprocessing(dpath, cpath, dataNum2)
    return 0

# @cached_property
@celery.task(name='psycho_2_7.backtasks.trainings')
def trainings(dataid, modelid, tname, epochs, batch):
    #sys.path.insert(0, '/home/imr-ai/psycho_2_7/ProjectEn/backend_test')
    # from train_anomaly2 import training

    #reset_keras()
    #with tf.device("/job:local/task:0"):

    # training(dataid, modelid, tname, epochs, batch)
    # tf.reset_default_graph()

    # sys.path.insert(0, '/home/imr-ai/psycho_2_7/ProjectEn/backend_test')
    # from train_anomaly2 import training
    #
    # training(dataid, modelid, tname, epochs, batch)
    return 0


    # K.clear_session()





    # sess = tf.Session(config=tf.ConfigProto(log_device_placement=True))
    # with tf.device('/gpu:1'):
    #     training(dataid, modelid, tname, epochs, batch)


    # with tf.Graph().as_default():
    #     gpu_options = tf.GPUOptions(allow_growth=True)



    print("finished")
    #tf.Session().reset("grpc://localhost:2222")



def tests(dataid,modelid,testid,trainname):
    # sys.path.insert(0, '/home/imr-ai/psycho_2_7/ProjectEn/anomaly_check')
    # from anomaly_check3 import test
    #
    # test(dataid,modelid,testid,trainname)
    return 0