import pandas as pd
import numpy as np
import resource

# sys.path.insert(0, '/home/uk/PredictionServer')
from API.api_helper.user_directory import folder_path, root_path
from functools import wraps


# # # # # # # # # # # # # # # # # # # # # # # #
#              F u n c t i o n s              #
# # # # # # # # # # # # # # # # # # # # # # # #
import time

import lightgbm as lgb
from sklearn.model_selection import RandomizedSearchCV

_, hard = resource.getrlimit(resource.RLIMIT_DATA)
resource.setrlimit(resource.RLIMIT_DATA, (12000, hard))
# resource.setrlimit(resource.RLIMIT_NPROC, (1,1))
# resource.setrlimit(resource.RLIMIT_CPU, (1,2))
# param = {
#         'num_leaves': 7,
#         'max_bin': 119,
#         'min_data_in_leaf': 6,
#         'learning_rate': 0.03,
#         'min_sum_hessian_in_leaf': 0.00245,
#         'bagging_fraction': 1.0,
#         'bagging_freq': 5,
#         'feature_fraction': 0.05,
#         'lambda_l1': 4.972,
#         'lambda_l2': 2.276,
#         'min_gain_to_split': 0.65,
#         # 'max_depth': 14,
#         'save_binary': True,
#         'seed': 1337,
#         'feature_fraction_seed': 1337,
#         'bagging_seed': 1337,
#         'drop_seed': 1337,
#         'data_random_seed': 1337,
#         'objective': 'binary',
#         'boosting_type': 'gbdt',
#         'verbose': 1,
#         'metric': 'auc',
#         'is_unbalance': True,
#         'boost_from_average': False,
#         'device': 'gpu',
#         'gpu_platform_id': 0,
#         'gpu_device_id': 0
#     }

def train_boosting_model(trainX, trainY):
    '''
    This function trains a model.
     Args:
        trainX: np.array, input feature
        trainY: np.array, label
    Returns:
        model: a trained model
    '''

    # RandomSearch w/ lightgbm model
    params = {
        'max_depth': [2, 3, 4, 5, 6],
        'learning_rate': [0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3],
        'n_estimators': [10, 50, 100, 200, 300, 400, 500],
        'num_leaves': [10, 20, 30, 40],
        'min_child_weight': [0.01, 0.02, 0.03, 0.04, 0.05],
        'device': 'gpu',
        'gpu_platform_id': 0,
        'gpu_device_id': 0
    }
    # define a lightgbm model
    lgb_model = lgb.LGBMRegressor(boosting_type='gbdt')

    # define a randomizedSearchCV
    random_search = RandomizedSearchCV(lgb_model, params, cv=12, iid=True)

    # conduct a randomized search
    random_search.fit(trainX, trainY)

    # return a model showing the best performance
    return random_search.best_estimator_


import os
import re
from calendar import monthrange


def get_test_data(area, pred_mode, start_year, start_month, start_day, date):
    '''
    This function generate test data by reading corresponding forecast data.
    Args:
        area: string, target area of prediction
        pred_mode: int, prediction mode (1: short-term prediction, 2: mid-term prediction)
    '''

    # get the number of subscribers from the latest sub data
    # - find the latest year of available sub data
    sub_file_list = os.listdir(folder_path + 'data/sub')
    sub_year_list = []
    for sub_file in sub_file_list:
        sub_number = re.findall("\d+", sub_file)
        if len(sub_number) > 0:
            sub_year_list.append(sub_number[0])
    sub_latest_year = int(max(sub_year_list))

    # - load the identified latest sub data
    sub_data = pd.read_csv(folder_path + 'data/sub/%s_sub_%d' % (area, sub_latest_year), delim_whitespace=True)
    last_sub_data = sub_data.tail(1)
    sub_same_date_data = last_sub_data.filter(regex=("sub.*"))

    date_vaule = date_normalization(start_year, start_month, start_day)

    # load the forecast data
    testX = []
    if pred_mode == 1:

        # - load the short-term forecast data
        # TODO: need to crawl forecast data and store the forecast into the following location
        # short_term_data = pd.read_csv(folder_path+'data/forecast/%s_%s_short_term'%(area, date_vaule), delim_whitespace=True)
        short_term_data = pd.read_csv(folder_path + 'data/forecast/%s/%s_short_term' % (date, area),
                                      delim_whitespace=True)
        # print("short_term_data: ",short_term_data)
        for index, row in short_term_data.iterrows():
            avgTemp = row['avgTemp']
            maxTemp = row['maxTemp']
            minTemp = row['minTemp']

            temp_list = np.array([avgTemp, minTemp, maxTemp])
            # print("temp_list: ",temp_list)
            train_tmp = np.concatenate((temp_list, sub_same_date_data.values[0]))
            # print("train_tmp: ",train_tmp)
            testX.append(train_tmp)
            # print("testX: ", testX)

    elif pred_mode == 2:

        # - load the mid-term forecast data
        # TODO: need to crawl forecast data and store the forecast into the following location
        # mid_term_data = pd.read_csv(folder_path+'data/forecast/%s_%s_mid_term'%(area, date_vaule), delim_whitespace=True)
        mid_term_data = pd.read_csv(folder_path + 'data/forecast/%s/%s_mid_term' % (date, area),
                                    delim_whitespace=True)
        for index, row in mid_term_data.iterrows():
            avgTemp = row['avgTemp']
            maxTemp = row['maxTemp']
            minTemp = row['minTemp']

            temp_list = np.array([avgTemp, minTemp, maxTemp])
            train_tmp = np.concatenate((temp_list, sub_same_date_data.values[0]))
            testX.append(train_tmp)

    return testX


import datetime
import os


def get_train_data(area, start_year, start_month):
    '''
    This function generate train data.
    Args:
        area: string, target area of prediction
        start_year: int, target year of prediction
        start_month: int, target month of prediction
    '''

    # true data before start_year.start_month should be used
    target = datetime.date(start_year, start_month, 1)
    target = target - datetime.timedelta(days=25)

    for tyear in range(target.year - 4, target.year + 1):

        # load the weather data
        temp_data_tmp = pd.read_csv(folder_path + 'data/weather/%s_weather_%d' % (area, tyear), delim_whitespace=True)
        if tyear == target.year - 4:
            temp_data = temp_data_tmp
        else:
            temp_data = temp_data.append(temp_data_tmp)

        # load the insu data
        insu_data_tmp = pd.read_csv(folder_path + 'data/insu/%s_insu_%d' % (area, tyear), delim_whitespace=True)
        if tyear == target.year - 4:
            insu_data = insu_data_tmp
        else:
            insu_data = insu_data.append(insu_data_tmp)

        # load the sub data
        sub_data_tmp = pd.read_csv(folder_path + 'data/sub/%s_sub_%d' % (area, tyear), delim_whitespace=True)
        if tyear == target.year - 4:
            sub_data = sub_data_tmp
        else:
            sub_data = sub_data.append(sub_data_tmp)

        # load the daily insu data
        insu_data_tmp = pd.read_csv(folder_path + 'data/insu/%s_insu_%d' % (area, tyear), delim_whitespace=True)
        if tyear == target.year - 4:
            insu_data = insu_data_tmp
        else:
            insu_data = insu_data.append(insu_data_tmp)

    trainX = []
    trainY = []
    for tyear in range(target.year - 4, target.year + 1):
        if tyear < start_year:
            mon_list = range(1, 13)
        elif tyear == start_year:
            mon_list = range(1, start_month)

        # print(mon_list)

        for tmon in mon_list:
            mon_days = monthrange(tyear, tmon)[1]
            for tday in range(1, mon_days + 1):
                temp_same_year = temp_data[temp_data['year'] == tyear]
                temp_same_month = temp_same_year[temp_same_year['month'] == tmon]
                temp_same_date = temp_same_month[temp_same_month['date'] == tday]

                avgTemp = temp_same_date['avgTemp'].values[0]
                minTemp = temp_same_date['minTemp'].values[0]
                maxTemp = temp_same_date['maxTemp'].values[0]

                sub_same_year = sub_data[sub_data['year'] == tyear]
                sub_same_month = sub_same_year[sub_same_year['month'] == tmon]
                sub_same_date = sub_same_month[sub_same_month['date'] == tday]
                sub_same_date_data = sub_same_date.filter(regex=("sub.*"))

                insu_same_year = insu_data[insu_data['year'] == tyear]
                # print("insu_same_year: ", insu_same_year)
                insu_same_month = insu_same_year[insu_same_year['month'] == tmon]
                insu_same_date = insu_same_month[insu_same_month['date'] == tday]
                # print("insu_same_date: ",insu_same_date)
                insu_daily = insu_same_date['insu_sum'].values[0]
                # print("insu_daily: ", insu_daily)

                temp_list = np.array([avgTemp, minTemp, maxTemp])
                train_tmp = np.concatenate((temp_list, sub_same_date_data.values[0]))
                trainX.append(train_tmp)
                trainY.append(insu_daily)

    return trainX, trainY

def prepare_a_model(area, start_year, start_month):
    '''
    This function trains a prediction model to be used for short-term and mid-term predictions.
    Args:
        area: string, target area of prediction
        start_year: int, start year of prediction
        start_month: int, start month of precition
    '''

    # prepare data
    trainX, trainY = get_train_data(area, start_year, start_month)

    # train a model
    trained_model = train_boosting_model(trainX, trainY)

    return trained_model


def predict_short_term(pred_model, area, start_year, start_month, start_day, date):
    '''
    This function predicts 3 days using DONG-NAE forecast (i.e., 3 days from today including today)
    Args:
        pred_model: estimator, a trained model
        area: string, target area of prediction
    '''

    # prepare data
    testX = get_test_data(area, 1, start_year, start_month, start_day, date)

    # conduct prediction
    pred = pred_model.predict(testX)

    return np.array(pred)


def predict_mid_term(pred_model, area, start_year, start_month, start_day, date):
    '''
    This function predicts 8 days using JUNG-GI forecast in addition to predict_three_days (i.e., predict from today+4 to today+11)
    Args:
        pred_model: estimator, a trained model
        area: string, target area of prediction
    '''

    # prepare data
    testX = get_test_data(area, 2, start_year, start_month, start_day, date)

    # conduct prediction
    pred = pred_model.predict(testX)

    return np.array(pred)


import prediction.prediction_ETRI.predict_coming_30days as predict_coming_30days


def predict_long_term(area, start_year, start_month, start_day):
    '''
    This function predicts a month using another function defined in 'predict_HyGas_naju_24months' file. The prediction results from today+12 to the last will be used.
    Args:
        area: string, target area of prediction
        start_year: int, start year of prediction
        start_month: int, start month of prediction
        start_day: int, start day of prediction
    '''

    pred = predict_coming_30days.conduct_prediction(area, start_year, start_month, start_day)

    return np.array(pred)


def date_normalization(start_year, start_month, start_day):
    value = '%4d%02d%02d' % (start_year, start_month, start_day)
    return value


# # # # # # # # # # # # # # # # # # # # # # # #
#                M a i n                      #
# # # # # # # # # # # # # # # # # # # # # # # #

def main(area, start_year, start_month, start_day, date, user_key, detectkey):
    # print("aa")
    print("predict_daily_start")
    pred_model = prepare_a_model(area, start_year, start_month)

    print("----- ing -----")
    # print("pred_model: ", pred_model)

    pred_short = predict_short_term(pred_model, area, start_year, start_month, start_day, date)
    # print("pred_short: ", pred_short)
    pred_mid = predict_mid_term(pred_model, area, start_year, start_month, start_day, date)
    # print("pred_mid: ", pred_mid)
    ## 30일 예측 이어서 30고정.
    pred_long_year = start_year - 1
    pred_long = predict_long_term(area, pred_long_year, start_month, 30)
    # print("pred_long: ", pred_long)

    # 현재 예측 단기/중기 .csv 저장소 -> 'naju_mid_term_2019_10_03' 형식으로
    pred_temp = np.concatenate((pred_short, pred_mid), axis=None)
    # print("pred_temp: ", pred_temp)
    pred_all = np.concatenate((pred_temp, pred_long[len(pred_temp):]), axis=None)
    # print("pred_all: ", pred_all)
    # - prepare the output file for monthly prediction

    # print(pred_all[5])
    # print("pred_all: ",pred_all)
    # kwda=list(pred_all)
    # print(kwda)
    # print(type(kwda))

    folder = folder_path + 'result/%d' % (user_key)
    if not os.path.isdir(folder):
        os.makedirs(folder)

    # print("main_start_day: ", start_day)

    daily_output_file = folder_path + 'result/%d/predict_%s_%d_%d_%d_daily' % (user_key, area, start_year, start_month, start_day)
    daily_f = open(daily_output_file, 'w')

    daily_f.write(str(pred_all))
    daily_f.close()

    filepath = root_path + '/detectkey/'

    message=str(detectkey)
    print(detectkey)

    if not os.path.isdir(filepath):
        os.mkdir(filepath)
    with open(filepath+message,'w') as f:
        f.write(message)

    print("predict_daily_done")

main('naju',2019,10,30,20191112,1,1)
# if  __name__ == '__main__' :
#     t = multiprocessing.Process(target=main, args=("Process-1",180))
#     t.start()
#     t.join()