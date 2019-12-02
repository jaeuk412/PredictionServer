import pandas as pd
import numpy as np

# # # # # # # # # # # # # # # # # # # # # # # #
#              F u n c t i o n s              #
# # # # # # # # # # # # # # # # # # # # # # # #

import lightgbm as lgb
from sklearn.model_selection import RandomizedSearchCV
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
		'min_child_weight':[0.01, 0.02, 0.03, 0.04, 0.05] 
	} 
	# define a lightgbm model
	lgb_model = lgb.LGBMRegressor(boosting_type='gbdt') 

	# define a randomizedSearchCV
	random_search = RandomizedSearchCV(lgb_model, params, cv=12, iid=True) 
	
	# conduct a randomized search
	random_search.fit(trainX, trainY)

	# return a model showing the best performance
	return random_search.best_estimator_


def predict_three_days(area, start_year, start_month, start_day):
	'''
	This function predicts 3 days using DONG-NAE forecast (i.e., 3 days from today including today)
	Args:
		area: string, target area of prediction
		start_year: int, start year of prediction
		start_month: int, start month of precition
		start_day: int, start day of prediction	
	'''


def predict_eight_days(area, start_year, start_month, start_day):
	'''
	This function predicts 8 days using JUNG-GI forecast in addition to predict_three_days (i.e., predict from today+4 to today+11)
	Args:
		area: string, target area of prediction
		start_year: int, start year of prediction
		start_month: int, start month of precition
		start_day: int, start day of prediction	
	'''


import predict_HyGas_naju_24months
def predict_month(area, start_year, start_month):
	'''
	This function predicts a month using another function defined in 'predict_HyGas_naju_24months' file. The prediction results from today+12 to the last will be used.
	Args:
		area: string, target area of prediction
		start_year: int, start year of prediction
		start_month: int, start month of prediction
	'''
	daily_pred = predict_HyGas_naju_24months.main(area, start_year, start_month, 1, 0, 0)
	print (daily_pred)

area = 'naju'
for tyear in range(2014, 2018+1): 

	# load the weather data
	temp_data_tmp = pd.read_csv('data/weather/%s_weather_%d'%(area, tyear), delim_whitespace=True) 
	if tyear == 2014:
		temp_data = temp_data_tmp 
	if tyear > 2014: 
		temp_data = temp_data.append(temp_data_tmp)

	# load the insu and sub data 
	insu_sub_data_tmp = pd.read_csv('data/insu_sub/%s_insu_sub_%d'%(area, tyear), delim_whitespace=True) 
	if tyear == 2014:
		insu_sub_data = insu_sub_data_tmp 
	if tyear > 2014: 
		insu_sub_data = insu_sub_data.append(insu_sub_data_tmp)

	# load the daily insu data 
	insu_data_tmp = pd.read_csv('data/insu/%s_insu_%d'%(area, tyear), delim_whitespace=True) 
	if tyear == 2014:
		insu_data = insu_data_tmp 
	if tyear > 2014: 
		insu_data = insu_data.append(insu_data_tmp)


trainX = []
trainY = []
from calendar import monthrange
for tyear in range(2014, 2018+1):
	if tyear < 2018:
		mon_list = range(1,13)
	elif tyear == 2018:
		mon_list = range(1,12)

	for tmon in mon_list: 
		mon_days = monthrange(tyear, tmon)[1] 
		for tday in range(1, mon_days+1): 
			temp_same_year = temp_data[temp_data['year']==tyear] 
			temp_same_month = temp_same_year[temp_same_year['month']==tmon]
			temp_same_date = temp_same_month[temp_same_month['date']==tday]
			avgTemp = temp_same_date['avgTemp'].values[0]
			minTemp = temp_same_date['minTemp'].values[0]
			maxTemp = temp_same_date['maxTemp'].values[0]

			insu_sub_same_year = insu_sub_data[insu_sub_data['year']==tyear] 
			insu_sub_same_month = insu_sub_same_year[insu_sub_same_year['month']==tmon]
			insu_sub_same_date = insu_sub_same_month[insu_sub_same_month['date']==tday]
			insu_sub_same_date_data = insu_sub_same_date.filter(regex=("sub.*"))

			insu_same_year = insu_data[insu_data['year']==tyear] 
			insu_same_month = insu_same_year[insu_same_year['month']==tmon]
			insu_same_date = insu_same_month[insu_same_month['date']==tday]
			insu_daily = insu_same_date['insu'].values[0]

			temp_list = np.array([avgTemp, minTemp, maxTemp])
			train_tmp = np.concatenate((temp_list, insu_sub_same_date_data.values[0]))
			trainX.append(train_tmp)
			trainY.append(insu_daily)

trained_model = train_boosting_model(trainX, trainY)

testX = []
testY = []
from calendar import monthrange
for tyear in range(2018, 2018+1):
	mon_list = range(12,13)

	for tmon in mon_list: 
		mon_days = monthrange(tyear, tmon)[1] 
		for tday in range(1, mon_days+1): 
			temp_same_year = temp_data[temp_data['year']==tyear] 
			temp_same_month = temp_same_year[temp_same_year['month']==tmon]
			temp_same_date = temp_same_month[temp_same_month['date']==tday]
			avgTemp = temp_same_date['avgTemp'].values[0]
			minTemp = temp_same_date['minTemp'].values[0]
			maxTemp = temp_same_date['maxTemp'].values[0]

			insu_sub_same_year = insu_sub_data[insu_sub_data['year']==tyear] 
			insu_sub_same_month = insu_sub_same_year[insu_sub_same_year['month']==tmon]
			insu_sub_same_date = insu_sub_same_month[insu_sub_same_month['date']==tday]
			insu_sub_same_date_data = insu_sub_same_date.filter(regex=("sub.*"))

			insu_same_year = insu_data[insu_data['year']==tyear] 
			insu_same_month = insu_same_year[insu_same_year['month']==tmon]
			insu_same_date = insu_same_month[insu_same_month['date']==tday]
			insu_daily = insu_same_date['insu'].values[0]

			temp_list = np.array([avgTemp, minTemp, maxTemp])
			train_tmp = np.concatenate((temp_list, insu_sub_same_date_data.values[0]))
			testX.append(train_tmp)
			testY.append(insu_daily)

pred = trained_model.predict(testX)
for idx in range(len(pred)):
	print ("%.2f %.2f , %.2f"%(pred[idx], testY[idx], abs(pred[idx]-testY[idx])*100/testY[idx]))
print ("%.2f"%(np.mean(abs(pred-testY)*100/testY)))
