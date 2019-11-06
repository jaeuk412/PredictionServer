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


from calendar import monthrange
def get_train_test_data(area, start_year, start_month, start_day, num_days):
	'''
	Current code is only for the purpose of test.
	It should be re-programmed.
	'''

	for tyear in range(start_year-4, start_year+1): 

		# load the weather data
		temp_data_tmp = pd.read_csv('data/weather/%s_weather_%d'%(area, tyear), delim_whitespace=True) 
		if tyear == start_year-4:
			temp_data = temp_data_tmp 
		else:
			temp_data = temp_data.append(temp_data_tmp)

		# load the insu data 
		insu_data_tmp = pd.read_csv('data/insu/%s_insu_%d'%(area, tyear), delim_whitespace=True) 
		if tyear == start_year-4:
			insu_data = insu_data_tmp 
		else:
			insu_data = insu_data.append(insu_data_tmp)

		# load the sub data 
		sub_data_tmp = pd.read_csv('data/sub/%s_sub_%d'%(area, tyear), delim_whitespace=True) 
		if tyear == start_year-4:
			sub_data = sub_data_tmp 
		else:
			sub_data = sub_data.append(sub_data_tmp)

		# load the daily insu data 
		insu_data_tmp = pd.read_csv('data/insu/%s_insu_%d'%(area, tyear), delim_whitespace=True) 
		if tyear == start_year-4:
			insu_data = insu_data_tmp 
		else:
			insu_data = insu_data.append(insu_data_tmp)


	trainX = []
	trainY = []
	# just for test
	for tyear in range(start_year-4, start_year+1):
		if tyear < start_year:
			mon_list = range(1,13)
		elif tyear == start_year:
			mon_list = range(1,start_month)

		for tmon in mon_list: 
			mon_days = monthrange(tyear, tmon)[1] 
			for tday in range(1, mon_days+1): 
				temp_same_year = temp_data[temp_data['year']==tyear] 
				temp_same_month = temp_same_year[temp_same_year['month']==tmon]
				temp_same_date = temp_same_month[temp_same_month['date']==tday]
				avgTemp = temp_same_date['avgTemp'].values[0]
				minTemp = temp_same_date['minTemp'].values[0]
				maxTemp = temp_same_date['maxTemp'].values[0]

				sub_same_year = sub_data[sub_data['year']==tyear] 
				sub_same_month = sub_same_year[sub_same_year['month']==tmon]
				sub_same_date = sub_same_month[sub_same_month['date']==tday]
				sub_same_date_data = sub_same_date.filter(regex=("sub.*"))

				insu_same_year = insu_data[insu_data['year']==tyear] 
				insu_same_month = insu_same_year[insu_same_year['month']==tmon]
				insu_same_date = insu_same_month[insu_same_month['date']==tday]
				insu_daily = insu_same_date['insu_sum'].values[0]

				temp_list = np.array([avgTemp, minTemp, maxTemp])
				train_tmp = np.concatenate((temp_list, sub_same_date_data.values[0]))
				trainX.append(train_tmp)
				trainY.append(insu_daily)

	testX = []
	testY = []
	for tyear in range(start_year, start_year+1):
		mon_list = range(start_month, start_month+1)

		for tmon in mon_list: 
			mon_days = monthrange(tyear, tmon)[1] 
			for tday in range(1, mon_days+1): 
				temp_same_year = temp_data[temp_data['year']==tyear] 
				temp_same_month = temp_same_year[temp_same_year['month']==tmon]
				temp_same_date = temp_same_month[temp_same_month['date']==tday]
				avgTemp = temp_same_date['avgTemp'].values[0]
				minTemp = temp_same_date['minTemp'].values[0]
				maxTemp = temp_same_date['maxTemp'].values[0]

				sub_same_year = sub_data[sub_data['year']==tyear] 
				sub_same_month = sub_same_year[sub_same_year['month']==tmon]
				sub_same_date = sub_same_month[sub_same_month['date']==tday]
				sub_same_date_data = sub_same_date.filter(regex=("sub.*"))

				insu_same_year = insu_data[insu_data['year']==tyear] 
				insu_same_month = insu_same_year[insu_same_year['month']==tmon]
				insu_same_date = insu_same_month[insu_same_month['date']==tday]
				insu_daily = insu_same_date['insu_sum'].values[0]

				temp_list = np.array([avgTemp, minTemp, maxTemp])
				train_tmp = np.concatenate((temp_list, sub_same_date_data.values[0]))
				testX.append(train_tmp)
				testY.append(insu_daily)

	return trainX, trainY, testX, testY


def predict_three_days(area, start_year, start_month, start_day, num_days):
	'''
	This function predicts 3 days using DONG-NAE forecast (i.e., 3 days from today including today)
	Args:
		area: string, target area of prediction
		start_year: int, start year of prediction
		start_month: int, start month of precition
		start_day: int, start day of prediction	
	'''

	# prepare data
	trainX, trainY, testX, testY = get_train_test_data(area, start_year, start_month, start_day, num_days)

	# train a model
	trained_model = train_boosting_model(trainX, trainY)

	# predict
	testX = testX[:3]
	testY = testY[:3]
	pred = trained_model.predict(testX)

	for idx in range(len(pred)):
		print ("%.2f %.2f , %.2f"%(pred[idx], testY[idx], abs(pred[idx]-testY[idx])*100/testY[idx]))
	print ("%.2f"%(np.mean(abs(pred-testY)*100/testY)))

	# return
	return pred

def predict_eight_days(area, start_year, start_month, start_day, num_days):
	'''
	This function predicts 8 days using JUNG-GI forecast in addition to predict_three_days (i.e., predict from today+4 to today+11)
	Args:
		area: string, target area of prediction
		start_year: int, start year of prediction
		start_month: int, start month of precition
		start_day: int, start day of prediction	
	'''

	# prepare data
	trainX, trainY, testX, testY = get_train_test_data(area, start_year, start_month, start_day, num_days)

	# train a model
	trained_model = train_boosting_model(trainX, trainY)

	# predict
	testX = testX[3:11]
	testY = testY[3:11]
	pred = trained_model.predict(testX)

	for idx in range(len(pred)):
		print ("%.2f %.2f , %.2f"%(pred[idx], testY[idx], abs(pred[idx]-testY[idx])*100/testY[idx]))
	print ("%.2f"%(np.mean(abs(pred-testY)*100/testY)))

	# return
	return pred


import predict_HyGas_naju_24months
def predict_month(area, start_year, start_month, start_day, num_days):
	'''
	This function predicts a month using another function defined in 'predict_HyGas_naju_24months' file. The prediction results from today+12 to the last will be used.
	Args:
		area: string, target area of prediction
		start_year: int, start year of prediction
		start_month: int, start month of prediction
	'''
	daily_pred = predict_HyGas_naju_24months.main(area, start_year, start_month, 1, 0, 0)
	
	return daily_pred[11:30]



pred_three_days = predict_three_days('naju', 2018, 12, 1, 3)
pred_eight_days = predict_eight_days('naju', 2018, 12, 4, 8)
pred_month_res = predict_month('naju', 2018, 12, 12, 18)

print (pred_three_days)
print (pred_eight_days)
print (pred_month_res)
