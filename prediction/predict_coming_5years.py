# -*- coding: utf-8 -*-
# 대상 지역의 년별 총 인수량 예측(월별의 누적)
# 가지고 있는 데이터: 5년치 인수량 데이터
# 입력 변수: area, current_year_and_month(예측하거자하는 기간의 시작 년/월)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from API.api_helper.user_directory import folder_path, root_path
import os
import itertools # parameter search 할 때 사용

warnings.filterwarnings("ignore")

def main(area, year, start_date, user_key, detectkey):
    ### input ###
    print("----yearly_start----")
    # 이건 이후에 argment나 입력 변수로 받아야됨.
    # result_path = '/home/uk/PredictionServer/prediction/result/yearly/'
    if not os.path.isdir(folder_path + 'result/%d' % (user_key)):
        os.mkdir(folder_path + 'result/%d' % (user_key))

    if not os.path.isdir(folder_path + 'result/%d/yearly' % (user_key)):
        os.mkdir(folder_path + 'result/%d/yearly' % (user_key))

    result_path = folder_path + 'result/%d/yearly/' % (user_key)
    print(result_path)
    # area = 'naju'
    # current_year = 2019
    current_year = year

    def load_insu_data(area, current_year):
        insu_data_past_5years = pd.DataFrame()

        for tyear in range(current_year - 5, current_year):
            print('target_years: ', tyear)
            insu_data_tmp = pd.read_csv(folder_path + 'data/tmp_for_pred/insu/%s_insu_%d' % (area, tyear),
                                        delim_whitespace=True)
            print(insu_data_tmp.shape)
            insu_data_past_5years = insu_data_past_5years.append(
                insu_data_tmp)  # concat 쓸수도 있는데, 본래 코드에서 append를 주로 사용하셔서 통일함.

        return insu_data_past_5years

    insu_data_past_5years = load_insu_data(area, current_year)
    print(insu_data_past_5years.head(10))
    print(insu_data_past_5years.shape)

    insu_data_past_5years_sum = insu_data_past_5years[['year', 'month', 'date', 'insu_sum']]
    print(insu_data_past_5years_sum.head(10))
    print(insu_data_past_5years_sum.shape)

    print(insu_data_past_5years_sum.loc[
          (insu_data_past_5years_sum['year'] == 2014) & (insu_data_past_5years_sum['month'] == 1), :])

    insu_month = pd.DataFrame(columns=['Datetime', 'year', 'month', 'insu'])
    # print(insu_month)

    for year in range(current_year - 5, current_year):
        print('Year: ', year)
        for month in range(1, 12 + 1):
            print('Month: ', month)
            insu_monthly = insu_data_past_5years_sum.loc[
                           (insu_data_past_5years_sum['year'] == year) & (insu_data_past_5years_sum['month'] == month),
                           :]
            insu_monthly_sum = insu_monthly['insu_sum'].sum()
            print('sum: ', insu_monthly_sum)
            date_index = str(year) + '-' + str(month)
            # insu_month = insu_month.append(pd.DataFrame([[date_index, year, month, insu_monthly_sum]], columns=['Datetime', 'year', 'month', 'insu']), ignore_index=True)
            insu_month = insu_month.append(
                pd.DataFrame([[str(year), str(month), float(insu_monthly_sum)]], columns=['year', 'month', 'insu']),
                ignore_index=True)
            # 숫자가 int나 float으로 되야되는데 sum함수의 결과가 object여서 연산이 안된것!
            # 여기서 ignore_index 안하면 새로만들어진 데이터의 index가 유지되서 이 경우에는 한 row씩 생기기 때문에 전부 0으로 들어감

    insu_month['Datetime'] = pd.to_datetime(insu_month['year'] + '-' + insu_month['month'])
    insu_month = insu_month.set_index('Datetime')
    # https://stackoverflow.com/questions/27032052/how-do-i-properly-set-the-datetimeindex-for-a-pandas-datetime-object-in-a-datafr

    print(insu_month)
    print(insu_month.shape)
    print(insu_month.dtypes)

    # 2월 윤달로 인해 365일인 해가 있고, 366일인 해가 있는데, 현재는 년간 총량을 보는 거라 우선 이 부분은 배제, 이후에 필요하면 휴일 체크하듯이 체크해서 년별로 고려해줘야함.

    ### modeling #1 ###
    ### Classic Machine Learning ###
    from statsmodels.tsa.ar_model import AR  # tsa:time series analysis
    from statsmodels.tsa.arima_model import ARMA, ARIMA
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    from random import random
    from statsmodels.tsa.seasonal import seasonal_decompose
    import statsmodels.api as sm

    def draw_ts(timeSeries):
        f = plt.figure(facecolor='white')
        timeSeries.plot(color='blue')
        # plt.show()

    # draw_ts(insu_month.insu)
    # plt.show()

    def draw_trend(timeSeries, size):
        f = plt.figure(facecolor='white')
        rol_mean = timeSeries.rolling(window=size).mean()
        rol_weighted_mean = timeSeries.ewm(span=size).mean()
        timeSeries.plot(color='blue', label='Original')
        rol_mean.plot(color='red', label='Rolling Mean')
        rol_weighted_mean.plot(color='black', label='Weighted Rolling Mean')
        plt.legend(loc='best')
        plt.title('Rolling Mean')
        # plt.show()

    draw_trend(insu_month.insu, 5)
    # plt.show()
    plt.savefig(result_path + 'Original_Data' + '.png')

    error_total = []

    train_data = insu_month.insu

    decomposition = seasonal_decompose(train_data, model="additive")
    trend = decomposition.trend
    seasonal = decomposition.seasonal
    residual = decomposition.resid

    # stationary를 볼려면 trend, seasonmality 를 제거해야 알 수 있다.

    trend_fig = plt.figure(figsize=(10, 10))
    ax1 = trend_fig.add_subplot(311)
    trend.plot(color='blue', label='Trend')
    plt.legend(loc='upper left')
    plt.xlabel('Time')
    plt.ylabel('Gas_Qmonth')

    ax2 = trend_fig.add_subplot(312)
    seasonal.plot(color='red', label='Seasonal')
    plt.legend(loc='upper left')
    plt.xlabel('Time')
    plt.ylabel('Gas_Qmonth')

    ax3 = trend_fig.add_subplot(313)
    residual.plot(color='green', label='residual')  # linear 하게 경향을 받을 때 분산 정도로 이해하면 쉬움.
    plt.legend(loc='upper left')
    plt.xlabel('Time')
    plt.ylabel('Gas_Qmonth')
    # plt.subplots_adjust(0, 0, 1, 1, 0, 0)

    # plt.show()
    plt.savefig(result_path + 'Data_Feature' + '.png')

    model = SARIMAX(train_data, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))

    # print('train data:', train_data)
    model_fit = model.fit()
    print('len_traindata:', len(train_data))
    # print(train_data_x.tail(10))
    # print(train_data_x.describe())

    prediction_range_past = 30  #
    prediction_range_future = 60 - 1

    yhat = model_fit.get_prediction(start=len(train_data) - prediction_range_past,
                                    end=len(train_data) + prediction_range_future, dynamic=False)

    yhat_confidence = yhat.conf_int()  # confidence interval
    yhat = yhat.predicted_mean

    print('prediction:', yhat)
    print('prediction_shape:', yhat.shape)

    print('prediction_conf_int:', yhat_confidence)

    MSE = ((yhat.head(prediction_range_past) - train_data.tail(prediction_range_past)) ** 2).mean()
    print('MSE:', MSE)

    RMSE = np.sqrt(MSE)
    print('RMSE:', RMSE)

    print('max:', train_data.max())
    print('min:', train_data.min())
    print('range:', train_data.max() - train_data.min())

    error_rate = RMSE / (train_data.max() - train_data.min()) * 100
    error_rate = round(error_rate, 2)
    print('error_rate:' + str(error_rate) + ' %')

    error_total.append(error_rate)

    f = plt.figure(facecolor='white')
    plt.title('Gas-Qmonth_Prediction \n (RMSE: ' + str(RMSE) + ', error: ' + str(error_rate) + ' %)')

    train_data.plot(color='blue', marker='o', label='Original')  # 참고로 color와 style은 서로 wrapping 관계가 있어서 동시에 사용 못함.
    ax = yhat.plot(color='red', marker='o', label='Prediction')

    ax.fill_between(yhat_confidence.index, yhat_confidence.iloc[:, 0], yhat_confidence.iloc[:, 1], color='y', alpha=.5)
    plt.legend(loc='upper left')
    plt.xlabel('Time')
    plt.ylabel('Gas_Qmonth')

    ## show & save
    # plt.show()
    plt.savefig(result_path + '5years_Gas-insu_prediction' + '.png')

    print('error_total:')
    print(error_total)
    print('error_total_len:')
    print(len(error_total))
    error_total = [x for x in error_total if ~np.isnan(x)]  # nan 걸러네기.
    print('error_total_without Nan:')
    print(error_total)
    print('error_total_without Nan_len:')
    print(len(error_total))

    error_mean = np.mean(error_total)
    print('error_mean:' + str(error_mean) + ' %')

    # train_data.iloc[:, 0:10].plot()
    # plt.show()

    ### output list ###
    # 향후 5년 간 연별 총 인수량 5개(+월별 예측)
    # 사실 월별 예측으로 12개월 합산한걸 일년 총량으로 계산

    # 1) month type
    insu_coming_5years_monthly = pd.DataFrame(columns=['year', 'month', 'pred_monthly_insu'])
    output_monthly = yhat.iloc[-(prediction_range_future + 1):]
    i = 0
    print(output_monthly)
    print(output_monthly.shape)
    for year in range(current_year, current_year + 5, 1):
        for month in range(1, 12 + 1, 1):
            insu_coming_5years_monthly = insu_coming_5years_monthly.append(
                pd.DataFrame([[str(year), str(month), float(output_monthly[i])]],
                             columns=['year', 'month', 'pred_monthly_insu']),
                ignore_index=True)
            i = i + 1

    print(insu_coming_5years_monthly)
    print(insu_coming_5years_monthly.shape)

    insu_coming_5years_monthly.to_csv(
        result_path + 'coming_' + area + '_' + str(current_year) + '_to_' + str(current_year + 5) + '_monthly' + '.csv',
        mode='w', index=False, sep=' ')

    # 2) year type
    insu_coming_5years_yearly = pd.DataFrame(columns=['year', 'pred_yearly_insu'])
    prediction_year = current_year
    for one_year in range(1, 60, 12):
        sum_one_year = output_monthly.iloc[:one_year].sum()
        print(one_year)
        print(sum_one_year)
        insu_coming_5years_yearly = insu_coming_5years_yearly.append(
            pd.DataFrame([[str(prediction_year), float(sum_one_year)]], columns=['year', 'pred_yearly_insu']),
            ignore_index=True)
        prediction_year = prediction_year + 1

    # 연간 데이터가 현재 기준 12개월인지, 회계년도 기준 같은 연1월부터 12월까지 인지에 따라서 12개월을 짜르는 기준이 달라지는데
    # 현재는 입력한 년도부터 향후 5년에 대해 1월부터 12월까지를 기준으로 년간 데이터 합산 결과 만듬.
    output_yearly = insu_coming_5years_yearly
    # output_yearly = output_yearly.set_index('year')
    print(output_yearly)
    print(output_yearly.shape)
    output_yearly.to_csv(
        # result_path + 'coming_' + area + '_' + str(current_year) + '_to_' + str(current_year + 5) + '_yearly' + '.csv',
        mode='w', index=False, sep=' ')

    filepath = root_path + '/detectkey/'

    message = "yearly_" + str(detectkey)
    if not os.path.isdir(filepath):
        os.mkdir(filepath)
    with open(filepath + message, 'w') as f:
        f.write(message)
    print("----yearly_done----")

    # 최종 output: insu_coming_5years_monthly, output_yearly

# main('naju',2019,20191023,1)
