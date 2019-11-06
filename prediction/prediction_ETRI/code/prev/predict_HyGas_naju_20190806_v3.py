import pandas as pd
import numpy as np

# # # # # # # # # # # # # # # # # # # # # # # #
#              F u n c t i o n s              #
# # # # # # # # # # # # # # # # # # # # # # # #

from calendar import monthrange
def write_prediction_to_file(daily_output_file, target_year, tmon, daily_pred_insu_list, daily_true_insu_list, category_list):
	'''
	This function writes daily prediction result into file.
	Args:
		daily_output_file: string, output file name
		target_year: int, target year of prediction
		tmon: int, target month of prediction
		daily_pred_insu_list: np.array, daily predicted insu
		daily_true_insu_list: np.array, daily true insu
		category_list: list, a list of categories of prediction target
	'''

	f = open(daily_output_file, 'a+')

	# calculate the number of days of target_year.target_month
	mon_days = monthrange(target_year, tmon)[1] 

	# for each day
	for tday in range(1, mon_days+1): 
		data = "%d %d %d "%(target_year, tmon, tday)

		pred_insu_sum = 0
		true_insu_sum = 0
		# prediction result of each category
		for tidx in range(len(category_list)):
			data += "%.1f %.1f "%(daily_pred_insu_list[tidx][tday-1], daily_true_insu_list[tidx][tday-1])
			pred_insu_sum += daily_pred_insu_list[tidx][tday-1]
			true_insu_sum += daily_true_insu_list[tidx][tday-1]

		if true_insu_sum < 0:
			true_insu_sum = -1

		data += "%.1f %.1f\n"%(pred_insu_sum, true_insu_sum)

		f.write(data)

	f.close()


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

               
def predict_temp(area, target_year, target_mon, temp_mode):
	'''
	This function estimates temperature of target_year.target_month by averaging the temperature of the same date of recent 4 years.
	Args:
		area: string, target area of prediction
		target_year: int, the target year of prediction
		target_mon: int, the target month of prediction
		temp_mode: int, 0 - return the predicted temp, 1 - return the measured temp
	Returns:
		prev_avg_temp: np.array, predicted daily temperature of target_year.target_mon
	'''

	# return the predicted temp
	if temp_mode == 0:
		# manipulate weight for averaging temp. note that winter of Y2017 and Y2018 was colder than normal
		if target_year == 2019 and target_mon in [1, 2]:
			weight_list = [1, 1, 1, 0.3]
		else:
			weight_list = [1, 1, 1, 1]

		# read the temperature data of recent 4 years
		for tyear in range(target_year-4, target_year):
			try:
				temp_data_tmp = pd.read_csv('data/temperature/%s_temp_%d'%(area, tyear), delim_whitespace=True)
				# merge the read data into one data
				if tyear == target_year-4:
					temp_data = temp_data_tmp	
				if tyear > target_year-4:
					temp_data = temp_data.append(temp_data_tmp)
			except FileNotFoundError:
				print ("The required file [./data/temperature/%s_temp_%d] does not exist"%(area, tyear))
				# TODO: generate the required file
				return

		# get the number of days of target_year.target_month
		mon_days = monthrange(target_year, target_mon)[1] 

		prev_avg_temp = []
		# for each day of target_year.target_month
		for tday in range(1, mon_days+1): 
			prev_avg_temp_list = []
			
			# for recent 4 years
			for tyear in range(target_year-4, target_year):
				prev_same_year = temp_data[temp_data['year']== tyear]
				prev_same_month = prev_same_year[prev_same_year['month']==target_mon] 
				target_day = prev_same_month[prev_same_month['date']==tday] 

				avg_temp = target_day['avgTemp'].values[0] 
				prev_avg_temp_list.append(avg_temp)

			# averaging 'avgTemp' of recent 4 years
			prev_avg_temp.append( [np.mean(prev_avg_temp_list)] )

	# return the measured temp
	else:
		try:
			target_temp_data = pd.read_csv('data/temperature/%s_temp_%d'%(area, target_year), delim_whitespace=True)
		except FileNotFoundError:
			print ("The required file [./data/temperature/%s_temp_%d] does not exist"%(area, target_year))
			# TODO: generate the required file
			return

		# get the number of days of target_year.target_month
		mon_days = monthrange(target_year, target_mon)[1] 

		prev_avg_temp = []
		# for each day of target_year.target_month
		for tday in range(1, mon_days+1): 
			same_month = target_temp_data[target_temp_data['month']==target_mon] 
			target_day = same_month[same_month['date']==tday] 
			prev_avg_temp.append( [target_day['avgTemp'].values[0]] )

	# return daily predicted avgTemp
	return np.array(prev_avg_temp)


def predict_sub_num(area, cat, target_year, target_mon, sub_mode):
	'''
	This function estimates the number of subscribers of specified category of target_year.target_month by conducting curve fitting.
	Args:
		area: string, target area of prediction
		cat: string, target category of prediction
		target_year: int, the target year of prediction
		target_mon: int, the target month of prediction
		sub_mode: int, whether to use the predicted (0) or true data (1)
	Returns:
		float, the predicted number of subscribers
	'''

	# return the predicted number of subscribers
	if sub_mode == 0:
		# read the insu and sub data of recent 3 years
		for tyear in range(target_year-4, target_year):
			try:
				insu_sub_data_tmp = pd.read_csv('data/insu_sub/%s_insu_sub_%d'%(area, tyear), delim_whitespace=True)
				# merge the read data into one data
				if tyear == target_year-4:
					insu_sub_data = insu_sub_data_tmp	
				if tyear > target_year-4:
					insu_sub_data = insu_sub_data.append(insu_sub_data_tmp)
			except FileNotFoundError:
				print ("The required file [./data/insu_sub/%s_insu_sub_%d] does not exist"%(area, tyear))
				# TODO: need proper handling method
				return

		sub_num_list = []
	
		# for recent 4 years
		for tyear in range(target_year-4, target_year):
			prev_same_year = insu_sub_data[insu_sub_data['year']==tyear] 
			prev_same_month = prev_same_year[prev_same_year['month']==target_mon] 
			target_day = prev_same_month[prev_same_month['date']==1] 
			sub_num_list.append(target_day['sub_%s'%(cat)].values[0])

		# if all elements of sub_num_list are same, curve fitting is useless.
		if all(x == sub_num_list[0] for x in sub_num_list):
			return sub_num_list[0]
		# otherwise, conduct curve fitting.
		else:
			popt_a, popt_b = curve_fitting(range(1, len(sub_num_list)+1), sub_num_list)
			return popt_a * (len(sub_num_list)+1) + popt_b
	
	# return the true number of subscribers
	else:
		print ("")
		# TODO : prepare the file 


import lightgbm as lgb
import xgboost as xgb
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
def train_boosting_model(trainX, trainY): 
	''' 
	This function trains a model. 
	 Args: 
		trainX: np.array, input feature 
		trainY: np.array, label 
	Returns: 
		model: a trained model 
	'''

	'''
	# Define a xgboost model 
	xgb_model = xgb.XGBRegressor(booster='gbtree', max_depth=3, learning_rate=0.3, n_estimators=100, objective='reg:linear') 
	xgb_model.fit(trainX, trainY) 
	return xgb_model 

	# RandomSearch 
	params = { 
		'max_depth': [2, 3, 4], 
		'learning_rate': [0.05, 0.1, 0.2, 0.3], 
		'n_estimator': [30, 50, 100], 
		'gamma': [0, 0.1, 0.2, 0.3], 
		'min_child_weight':[1, 2, 3, 4, 5] 
	} 
	xgb_model = xgb.XGBRegressor(booster='gbtree', objective='reg:linear') 
	random_search = RandomizedSearchCV(xgb_model, params, cv=10, iid=True) 
	random_search.fit(trainX, trainY) 
	return random_search.best_estimator_ 
	''' 

	''' 
	# Define a lightgbm model 
	lgb_model = lgb.LGBMRegressor(boosting_type='gbdt', learning_rate=0.3, n_estimators=50) 
	lgb_model.fit(trainX, trainY) 
	return lgb_model 
	'''

	# RandomSearch 
	params = { 
		'max_depth': [2, 3, 4, 5, 6], 
		'learning_rate': [0.01, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3], 
		'n_estimators': [10, 50, 100, 200, 300, 400, 500], 
		'num_leaves': [10, 20, 30, 40], 
		'min_child_weight':[0.01, 0.02, 0.03, 0.04, 0.05] 
	} 
	lgb_model = lgb.LGBMRegressor(boosting_type='gbdt') 
	random_search = RandomizedSearchCV(lgb_model, params, cv=12, iid=True) 
	random_search.fit(trainX, trainY)
	return random_search.best_estimator_


def predict_avg_insu_by_temp_regression(area, cat, target_year, target_mon, temp_mode):
	'''
	This function predicts avg insu per subscriber of a specified category through temp-based regression.
	Args:
		area: string, target area of prediction
		cat: string, target category of prediction
		target_year: int, the target year of prediction
		target_mon: int, the target month of prediction
	Returns:
		pred_avg_insu: np.array, the predicted daily average insu per subscriber
	'''

	# group three months that typically show similar weather for better curve fitting
	if target_mon in [12, 1, 2]:
		mon_list = [12, 1, 2]
	elif target_mon in [3, 4, 5]:
		mon_list = [3, 4, 5]
	elif target_mon in [6, 7, 8]:
		mon_list = [6, 7, 8]
	elif target_mon in [9, 10, 11]:
		mon_list = [9, 10, 11]

	train_data = [] 
	train_label = [] 

	# use the data of recent 4 years for curve fitting
	for tyear in range(target_year-4, target_year):

		# read the temperature data
		try:
			temp_data = pd.read_csv('data/temperature/%s_temp_%d'%(area, tyear), delim_whitespace=True)
		except FileNotFoundError:
			print ("The required file [./data/temperature/%s_temp_%d] does not exist"%(area, tyear))
			# TODO: generate the required file
			return

		# read the insu and subscriber data
		try:
			insu_sub_data = pd.read_csv('data/insu_sub/%s_insu_sub_%d'%(area, tyear), delim_whitespace=True)
		except FileNotFoundError:
			print ("The required file [./data/insu_sub/%s_insu_sub_%d] does not exist"%(area, tyear))
			# TODO: need proper handling method
			return

		# read the date data
		try:
			date_data = pd.read_csv('data/date/date_info_Y%d'%(tyear), delim_whitespace=True)
		except FileNotFoundError:
			print ("The required file [./data/date/date_info_Y%d] does not exist"%(tyear))
			# TODO: generate the required file
			return

		# extract data realted to mon_list
		for tmon in mon_list: 

			# extract temperature data of the target month
			temp_data_month = temp_data[temp_data['month']==tmon] 

			# extract date data of the target month
			date_data_month = date_data[date_data['month']==tmon] 

			# extract insu and sub data of the target month
			insu_sub_data_month = insu_sub_data[insu_sub_data['month']==tmon] 
	
			# calculate the number of days of tyear.tmon
			mon_days = monthrange(tyear, tmon)[1] 

			# for each day of tyear.tmon
			for tday in range(1, mon_days+1): 

				# prepare train DATA
				# - get 'avgTemp' 
				temp_data_day = temp_data_month[temp_data_month['date']==tday] 
				avg_temp = temp_data_day['avgTemp'].values[0]
				# - get 'day' and 'holiday'
				date_data_day = date_data_month[date_data_month['date']==tday] 
				dayCode = date_data_day['day'].values[0]
				holidayCode = date_data_day['holiday'].values[0]
				#
				train_data.append([avg_temp, tmon, dayCode, holidayCode])
			
				# prepare train LABEL
				# - calculate the average insu per sub
				insu_sub_data_day = insu_sub_data_month[insu_sub_data_month['date']==tday] 
				insu_target = insu_sub_data_day['insu_%s'%(cat)].values[0] 
				sub_target = insu_sub_data_day['sub_%s'%(cat)].values[0] 
				#
				train_label.append(insu_target/sub_target)

	# train a boosting model
	trained_model = train_boosting_model(train_data, train_label)
	
	# get the predicted temperature of the target_year.target_mon
	prev_avg_temp = predict_temp(area, target_year, target_mon, temp_mode)

	# get the date info of target_year.target_mon
	try:
		date_data = pd.read_csv('data/date/date_info_Y%d'%(target_year), delim_whitespace=True)
	except FileNotFoundError:
		print ("The required file [./data/date/date_info_Y%d] does not exist"%(target_year))
		# TODO: generate the required file
		return
	# extract date data of the target month
	date_data_month = date_data[date_data['month']==target_mon] 
	#
	# calculate the number of days of tyear.tmon
	mon_days = monthrange(target_year, target_mon)[1] 
	#
	# for each day of tyear.tmon
	target_date_list = []
	for tday in range(1, mon_days+1): 
		date_data_day = date_data_month[date_data_month['date']==tday] 
		dayCode = date_data_day['day'].values[0]
		holidayCode = date_data_day['holiday'].values[0]
		target_date_list.append([target_mon, dayCode, holidayCode])

	# generate test data
	test_data = np.hstack([prev_avg_temp, target_date_list])

	# conduct prediction
	pred_avg_insu = trained_model.predict(test_data)

	return pred_avg_insu


def predict_avg_insu_by_averaging(area, cat, target_year, target_mon):
	'''
	This function predicts avg insu per sub by averaging data of recent 3 years
	Args:
		area: string, target area of prediction
		cat: string, target category of prediction
		target_year: int, the target year of prediction
		target_mon: int, the target month of prediction
	Returns:
		pred_avg_insu: np.array, the predicted daily average insu per subscriber
	'''

	# read the insu and sub data of recent 3 years
	for tyear in range(target_year-3, target_year):
		try:
			insu_sub_data_tmp = pd.read_csv('data/insu_sub/%s_insu_sub_%d'%(area, tyear), delim_whitespace=True)
			# merge the read data into one data for easy handling
			if tyear == target_year-3:
				insu_sub_data = insu_sub_data_tmp	
			if tyear > target_year-3:
				insu_sub_data = insu_sub_data.append(insu_sub_data_tmp)
		except FileNotFoundError:
			print ("The required file [./data/insu_sub/%s_insu_sub_%d] does not exist"%(area, tyear))
			# TODO: need proper handling method
			return

		try:
			date_data_tmp = pd.read_csv('data/date/date_info_Y%d'%(tyear), delim_whitespace=True)
			# merge the read data into one data for easy handling
			if tyear == target_year-3:
				date_data = date_data_tmp	
			if tyear > target_year-3:
				date_data = date_data.append(date_data_tmp)
		except FileNotFoundError:
			print ("The required file [./data/date/date_info_Y%d] does not exist"%(tyear))
			# TODO: generate the required file
			return

	prev_avg_insu = []

	# calculate the number of days of target_year.target_mon
	mon_days = monthrange(target_year, target_mon)[1] 

	try:
		target_date_data = pd.read_csv('data/date/date_info_Y%d'%(target_year), delim_whitespace=True)
	except FileNotFoundError:
		print ("The required file [./data/date/date_info_Y%d] does not exist"%(target_year))
		# TODO: generate the required file
		return

	# for each day of target_year.target_mmon
	for tday in range(1, mon_days+1): 

		same_month = target_date_data[target_date_data['month']==target_mon] 
		target_day = same_month[same_month['date']==tday] 
		c_holiday = target_day['holiday'].values[0]
		c_day = target_day['day'].values[0]

		# handle special case (i.e., 29 Feb)
		if target_mon == 2 and tday == 29:
			tday = 28

		prev_avg_insu_target = []

		# for recent 3 years
		for tyear in range(target_year-3, target_year):

			# Fine relevant dates
			# - Find the index of the same date in previous years 
			same_year = date_data[date_data['year']==tyear] 
			same_month = same_year[same_year['month']==target_mon] 
			same_date = same_month[same_month['date']==tday] 
			date_index = same_date.index.values 
			# 
			start_index = int(max(0, date_index-10)) 
			end_index = int(min(len(date_data), date_index+10)) 
			relevant_date_range = date_data.iloc[start_index:end_index] 
			# -- holiday or not 
			if c_holiday == 1:
				relevant_data = relevant_date_range[relevant_date_range['holiday']==c_holiday] 
				# -- some special holiday (e.g., election) does not exit in all years. In this case, we need to extract the data using 'day' code 
				if len(relevant_data) == 0: 
					relevant_data = relevant_date_range[relevant_date_range['day']==c_day] 
			else:
				relevant_data = relevant_date_range[relevant_date_range['day']==c_day] 


			prev_avg_insu_target_tmp = []
			# Extract insu_per_sub of the relevant dates
			for index, row in relevant_data.iterrows(): 
				t_mon = row['month'] 
				t_date = row['date']

				# handle special case (i.e., 29 Feb)
				if t_mon == 2 and t_date == 29:
					t_date = 28

				prev_same_year = insu_sub_data[insu_sub_data['year']== tyear]
				prev_same_month = prev_same_year[prev_same_year['month']==t_mon] 
				target_day = prev_same_month[prev_same_month['date']==t_date] 

				# get the average insu per sub	
				insu_target = target_day['insu_%s'%(cat)].values[0] 
				sub_target = target_day['sub_%s'%(cat)].values[0] 
				prev_avg_insu_target_tmp.append(insu_target/sub_target)
			prev_avg_insu_target.append(np.mean(prev_avg_insu_target_tmp))

		# delete useless data
		prev_avg_insu_target = np.array(prev_avg_insu_target)
		prev_avg_insu_target = prev_avg_insu_target[prev_avg_insu_target != 0.]

		# if 'prev_avg_insu_target' includes data, use the average
		if len(prev_avg_insu_target) > 0:
			prev_avg_insu.append( np.average(prev_avg_insu_target) )
		# otherwise, use 0
		else:
			prev_avg_insu.append(0)

	return np.array(prev_avg_insu)



def predict_avg_insu_by_curve_fitting(area, cat, target_year, target_mon):
	'''
	This function predicts avg insu per sub by conducting curve fitting with data of recent 3 years
	Args:
		area: string, target area of prediction
		cat: string, target category of prediction
		target_year: int, the target year of prediction
		target_mon: int, the target month of prediction
	Returns:
		pred_avg_insu: np.array, the predicted daily average insu per subscriber
	'''
	# read the insu and sub data of recent 3 years
	for tyear in range(target_year-3, target_year):
		try:
			insu_sub_data_tmp = pd.read_csv('data/insu_sub/%s_insu_sub_%d'%(area, tyear), delim_whitespace=True)
			# merge the read data into one data for easy handling
			if tyear == target_year-3:
				insu_sub_data = insu_sub_data_tmp	
			if tyear > target_year-3:
				insu_sub_data = insu_sub_data.append(insu_sub_data_tmp)
		except FileNotFoundError:
			print ("The required file [./data/insu_sub/%s_insu_sub_%d] does not exist"%(area, tyear))
			# TODO: need proper handling method
			return

		try:
			date_data_tmp = pd.read_csv('data/date/date_info_Y%d'%(tyear), delim_whitespace=True)
			# merge the read data into one data for easy handling
			if tyear == target_year-3:
				date_data = date_data_tmp	
			if tyear > target_year-3:
				date_data = date_data.append(date_data_tmp)
		except FileNotFoundError:
			print ("The required file [./data/date/date_info_Y%d] does not exist"%(tyear))
			# TODO: generate the required file
			return

	prev_avg_insu = []

	# calculate the number of days of target_year.target_mon
	mon_days = monthrange(target_year, target_mon)[1] 

	try:
		target_date_data = pd.read_csv('data/date/date_info_Y%d'%(target_year), delim_whitespace=True)
	except FileNotFoundError:
		print ("The required file [./data/date/date_info_Y%d] does not exist"%(target_year))
		# TODO: generate the required file
		return

	# for each day of target_year.target_mmon
	for tday in range(1, mon_days+1): 

		same_month = target_date_data[target_date_data['month']==target_mon] 
		target_day = same_month[same_month['date']==tday] 
		c_holiday = target_day['holiday'].values[0]
		c_day = target_day['day'].values[0]

		# handle special case (i.e., 29 Feb)
		if target_mon == 2 and tday == 29:
			tday = 28

		prev_avg_insu_target = []

		# for recent 3 years
		for tyear in range(target_year-3, target_year):

			# Fine relevant dates
			# - Find the index of the same date in previous years 
			same_year = date_data[date_data['year']==tyear] 
			same_month = same_year[same_year['month']==target_mon] 
			same_date = same_month[same_month['date']==tday] 
			date_index = same_date.index.values 
			# 
			start_index = int(max(0, date_index-10)) 
			end_index = int(min(len(date_data), date_index+10)) 
			relevant_date_range = date_data.iloc[start_index:end_index] 
			# -- holiday or not 
			if c_holiday == 1:
				relevant_data = relevant_date_range[relevant_date_range['holiday']==c_holiday] 
				# -- some special holiday (e.g., election) does not exit in all years. In this case, we need to extract the data using 'day' code 
				if len(relevant_data) == 0: 
					relevant_data = relevant_date_range[relevant_date_range['day']==c_day] 
			else:
				relevant_data = relevant_date_range[relevant_date_range['day']==c_day] 


			prev_avg_insu_target_tmp = []
			# Extract insu_per_sub of the relevant dates
			for index, row in relevant_data.iterrows(): 
				t_mon = row['month'] 
				t_date = row['date']

				# handle special case (i.e., 29 Feb)
				if t_mon == 2 and t_date == 29:
					t_date = 28

				prev_same_year = insu_sub_data[insu_sub_data['year']== tyear]
				prev_same_month = prev_same_year[prev_same_year['month']==t_mon] 
				target_day = prev_same_month[prev_same_month['date']==t_date] 

				# get the average insu per sub	
				insu_target = target_day['insu_%s'%(cat)].values[0] 
				sub_target = target_day['sub_%s'%(cat)].values[0] 
				prev_avg_insu_target_tmp.append(insu_target/sub_target)
			prev_avg_insu_target.append(np.mean(prev_avg_insu_target_tmp))

		# delete useless data
		prev_avg_insu_target = np.array(prev_avg_insu_target)
		prev_avg_insu_target = np.array(prev_avg_insu_target[prev_avg_insu_target != 0.])

		# if 'prev_avg_insu_target' includes more than one data, conduct curve fitting
		if len(prev_avg_insu_target) > 1:
			popt_a, popt_b = curve_fitting(range(1, len(prev_avg_insu_target)+1), prev_avg_insu_target)
			prev_avg_insu.append(popt_a * (len(prev_avg_insu_target)+1) + popt_b)
		# if 'prev_avg_insu_target' contains only one data, use that data
		elif len(prev_avg_insu_target) == 1:
			prev_avg_insu.append(prev_avg_insu_target[0])
		# otherwise, use 0
		else:
			prev_avg_insu.append(0)

	return np.array(prev_avg_insu)


def predict_avg_insu(area, cat, target_year, target_mon, temp_mode):
	'''
	This function estimates the average insu per subscriber of specified category of target_year.target_month through temmp-based linear regression.
	This function applies different prediction methods for target categories.
	Args:
		area: string, target area of prediction
		cat: string, target category of prediction
		target_year: int, the target year of prediction
		target_mon: int, the target month of prediction
	Returns:
		pred_avg_insu: np.array, the predicted daily average insu per subscriber
	'''

	# temp-based linear regression (i.e., input: temp, output: avg insu per sub)
	if cat in ['house', 'houseJHeating', 'salesTwo', 'industry']:

		return predict_avg_insu_by_temp_regression(area, cat, target_year, target_mon, temp_mode)

	# averaging data of recent 3 years
	elif cat in ['houseCooking', 'salesOne', 'bizHeating', 'bizCooling', 'heatFacility', 'heatCombined']:

		return predict_avg_insu_by_averaging(area, cat, target_year, target_mon)

	# curve fitting. 'CNG'
	else:
		return predict_avg_insu_by_curve_fitting(area, cat, target_year, target_mon)


def calc_errors(label, pred):
	'''
	This function calculates prediction errors:
	Args:
		label: np.array, daily true insu data
		pred: np.array, daily predicted insu data
	Returns:
		daily_mape: float, average of mape of daily prediction
		monthly_mape: float, mape of monthly prediction (i.e., sum of daily prediction)
		monthly_diff: float, difference between monthly true insu volume and monthly predicted insu volume
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
	
	if area == "naju":
		category = ['house', 'houseCooking', 'houseJHeating', 'salesOne', 'salesTwo', 'bizHeating', 'bizCooling', 'industry', 'heatFacility', 'heatCombined', 'CNG']

	return category


def estimate_insu_per_cat(area, cat, target_year, target_month, temp_mode, sub_mode):

	# Estimate daily insu per category
	# - get the predicted avg insu per sub
	pred_avg_insu = predict_avg_insu(area, cat, target_year, target_month, temp_mode)

	# - get the predicted subscriber number
	pred_sub_num = math.ceil(predict_sub_num(area, cat, target_year, target_month, sub_mode))

	# - estimate insu volume of target month. 'daily_cat_pred_insu' contains daily predicted insu
	daily_cat_pred_insu = pred_avg_insu * pred_sub_num


	is_true_exist = 1
	# Read the true daily insu if any
	try:
		true_insu_data = pd.read_csv('data/insu_sub/%s_insu_sub_%d'%(area, target_year), delim_whitespace=True)
	except FileNotFoundError:
		#print ("The required file [./data/insu_sub/%s_insu_sub_%d] does not exist"%(area, target_year))
		is_true_exist = 0

	# calculate the number of days of target_year.target_mon
	mon_days = monthrange(target_year, target_month)[1] 

	# for each day of target_year.target_mmon
	true_insu_list = []
	for tday in range(1, mon_days+1): 
		if is_true_exist == 1:
			same_month = true_insu_data[true_insu_data['month']== target_month]
			target_day = same_month[same_month['date']==tday] 
			true_insu_list.append(target_day['insu_%s'%(cat)].values[0] )
		else:
			true_insu_list.append(-1)

	return daily_cat_pred_insu, true_insu_list


import math
import datetime
def conduct_predict(area, start_year, start_month, month_range, temp_mode, sub_mode):
	'''
	This function conducts prediction.
	Args:
		area: string, target area of prediction
		start_year: int, start year of target prediction
		start_month: int, start month of target prediction
		month_range: int, the number of months to be predicted (e.g., prediction target => FROM start_year.start_month TO start_year.start_month + month_range)
	Returns:
		None.
	'''

	# a list of categories relevant to target area
	category = get_category(area)

	# prepare the output file for daily prediction
	daily_output_file = './result/%s_%d_%d_%d_T%d_S%d_daily'%(area, start_year, start_month, month_range, temp_mode, sub_mode)
	daily_f = open(daily_output_file, 'a+') 
	data = "year month date "
	for tidx in range(len(category)):
		data += "%s_pred %s_true "%(category[tidx], category[tidx])
	data += "pred_sum true_sum\n"
	daily_f.write(data)
	daily_f.close()

	# prepare the output file for monthly prediction
	monthly_output_file = './result/%s_%d_%d_%d_T%d_S%d_monthly'%(area, start_year, start_month, month_range, temp_mode, sub_mode)
	monthly_f = open(monthly_output_file, 'a+') 
	data = "year month "
	for tidx in range(len(category)):
		data += "%s_pred %s_true %s_mape "%(category[tidx], category[tidx], category[tidx])
	data += "pred_sum true_sum\n"
	monthly_f.write(data)

	# for each month from the start_year.start_month to start_year.start_month + month_range
	current = datetime.date(start_year, start_month, 1)
	current = current - datetime.timedelta(days=monthrange(current.year, current.month)[1])
	for ridx in range(1, month_range+1):
		current = current + datetime.timedelta(days=monthrange(current.year, current.month)[1])

		output_data = "%d %d "%(current.year, current.month)
		is_true_exist = 0
		monthly_pred_sum = 0
		monthly_true_sum = 0 
		daily_true_insu_list = [] # a list of true insu of all category of a target month. used for writing result into a file. 
		daily_pred_insu_list = [] # a list of predicted insu of all category of a targer month. used for writing result into a file.

		# for each category
		for cat in category:

			# estimate daily insu per category
			# 'true_insu' is an array of '-1' when there is no true data
			est_insu, true_insu = estimate_insu_per_cat(area, cat, current.year, current.month, temp_mode, sub_mode)
			
			monthly_pred_sum += np.sum(est_insu)

			# only when there is true data
			if true_insu[0] != -1:
				monthly_true_sum += np.sum(true_insu)
				is_true_exist = 1
			daily_true_insu_list.append(true_insu)
			daily_pred_insu_list.append(est_insu)

			# calculate prediction errors (only when there is true data)
			# '*mape' is -1 when there is no true data
			daily_mape, monthly_mape = calc_errors(true_insu, est_insu)
		
			# when there is true data
			if monthly_mape != -1:
				print ("%.1f %.1f %.1f , "%(np.sum(est_insu), np.sum(true_insu), monthly_mape), end='')
				output_data += "%.1f %.1f %.1f , "%(np.sum(est_insu), np.sum(true_insu), monthly_mape)
			# when there is no true data
			else:
				print ("%.1f -1 NA , "%(np.sum(est_insu)), end='')
				output_data += "%.1f -1 NA , "%(np.sum(est_insu))

		# when there is true data
		if is_true_exist == 1:
			print ("%.1f %.1f %.2f"%(monthly_pred_sum, monthly_true_sum, abs(monthly_true_sum-monthly_pred_sum)*100/monthly_true_sum)) 
			output_data += "%.1f %.1f %.2f\n"%(monthly_pred_sum, monthly_true_sum, abs(monthly_true_sum-monthly_pred_sum)*100/monthly_true_sum)
		# when there is no true data
		else:
			print ("%.1f -1.0 NA"%(monthly_pred_sum))
			output_data += "%.1f -1 NA\n"%(monthly_pred_sum)
		# write monthly prediction results into a file
		monthly_f.write(output_data)

		# write daily prediction results into a file
		write_prediction_to_file(daily_output_file, current.year, current.month, daily_pred_insu_list, daily_true_insu_list, category)

	monthly_f.close()


def check_and_prepare_data(area, start_year, start_month, month_range, temp_mode, sub_mode):





# # # # # # # # # # # # # # # # # # # # # # # #
#                M a i n                      #
# # # # # # # # # # # # # # # # # # # # # # # #
import sys

# target area of prediction (e.g., naju, gwangju, ....)
area = sys.argv[1] 

# start year of prediction (e.g., 2018)
start_year = int(sys.argv[2])

# start month of start year of prediction (e.g., 1)
start_month = int(sys.argv[3])

# the number of months to be predicted from start_year.start_month (e.g., 12 -> 12 months from 2018.1)
month_range = int(sys.argv[4])

# use the predicted temp or the measured temp (for the purpose of verification)
temp_mode = int(sys.argv[5])

# use the predicted subscriber number or the true numer (for the purpose of verification)
sub_mode = int(sys.argv[6])

# check whether the required files exist AND generate the required files if possible
check_and_prepare_data(area, start_year, start_month, month_range, temp_mode, sub_mode)

# conduct predictions
conduct_predict(area, start_year, start_month, month_range, temp_mode, sub_mode)
