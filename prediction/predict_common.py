import pandas as pd
import numpy as np
from API.api_helper.user_directory import folder_path

# # # # # # # # # # # # # # # # # # # # # # # #
#              F u n c t i o n s              #
# # # # # # # # # # # # # # # # # # # # # # # #

def func(x, a, b):
	'''
	This function is used for curve fitting.
	''' 
	return a*x + b

from scipy.optimize import curve_fit
import warnings
warnings.filterwarnings("ignore")
def curve_fitting(index_list, data_list):
	'''
	This function conucts a curve fitting. Find 'a' and 'b' of 'y = a*x + b'
	Args:
		index_list: np.array, X-axis values for linear regression
		data_list: np.array, Y-axis values for linear regression
	Returns:
		a and b: float	
	'''

	# conduct curve fitting (i.e., with y = a*x +b)
	popt, pcov = curve_fit(func, index_list, data_list) 

	return popt[0], popt[1]



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



def calc_errors(label, pred):
	'''
	This function calculates prediction errors:
	Args:
		label: np.array, daily true insu data
		pred: np.array, daily predicted insu data
	Returns:
		daily_mape: float, average of mape of daily prediction
		monthly_mape: float, mape of monthly prediction (i.e., sum of daily prediction)
	'''

	daily_mape_list = []
	monthly_label_sum = 0
	monthly_pred_sum = 0

	# for each day
	for idx in range(len(label)):
		if label[idx] > 0:
			daily_mape_list.append( abs(label[idx]-pred[idx])*100/label[idx] )

			monthly_label_sum += label[idx]
			monthly_pred_sum += pred[idx]

	# when there is no data (e.g., bizCooling)
	if len(daily_mape_list) == 0:
		daily_mape = -1
		monthly_mape = -1
	else:
		daily_mape = np.mean(daily_mape_list)
		monthly_mape = abs(monthly_label_sum - monthly_pred_sum)*100/monthly_label_sum

	return daily_mape, monthly_mape


def get_category(area):
	'''
	This function returns a list of categories for the target area.
	Args:
		area: string, target area of prediction
	Returns:
		category: list, a list of categories to be considered for prediction
	'''
	
	# TODO: need to add other areas

	if area == "naju":
		category = ['house', 'houseCooking', 'houseJHeating', 'salesOne', 'salesTwo', 'bizHeating', 'bizCooling', 'industry', 'heatFacility', 'heatCombined', 'CNG']

	else:
		print ("%s is not currely supported"%(area))
		return

	return category



# load the file
import prediction.get_date_info as get_date_info
def gen_date_file(target_year):
	'''
	This function generates a datee file.
	Args:
		target_year: int, target year of prediction
	'''

	get_date_info.get_date_main(target_year)



import prediction.crawling_temp as crawling_temp
def gen_temp_file(area, target_year):
	'''
    This function generates a temperature file.
    Args:
            area: string, target area of prediction
            target_year: int, target year of prediction
    '''

	crawling_temp.crawling_main(area, target_year)
