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

	# open the file to write the results
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

		# write the result to the file
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

		# load the temperature data of recent 4 years
		for tyear in range(target_year-4, target_year):
			# read the temp data
			temp_data_tmp = pd.read_csv('data/temperature/%s_temp_%d'%(area, tyear), delim_whitespace=True)
			# merge the read data into one data for easy processing
			if tyear == target_year-4:
				temp_data = temp_data_tmp	
			if tyear > target_year-4:
				temp_data = temp_data.append(temp_data_tmp)

		# get the number of days of target_year.target_month
		mon_days = monthrange(target_year, target_mon)[1] 

		# for each day of target_year.target_month
		prev_avg_temp = []
		for tday in range(1, mon_days+1): 
			prev_avg_temp_list = []
			
			# extract avgTemp from the data of recent 4 years
			for tyear in range(target_year-4, target_year):
				prev_same_year = temp_data[temp_data['year']== tyear]
				prev_same_month = prev_same_year[prev_same_year['month']==target_mon] 
				target_day = prev_same_month[prev_same_month['date']==tday] 

				avg_temp = target_day['avgTemp'].values[0] 
				prev_avg_temp_list.append(avg_temp)

			# averaging 'avgTemp' of recent 4 years
			prev_avg_temp.append( [np.mean(prev_avg_temp_list)] )

	# return the measured temp
	elif temp_mode == 1 :
		# read the true temp data
		target_temp_data = pd.read_csv('data/temperature/%s_temp_%d'%(area, target_year), delim_whitespace=True)

		# get the number of days of target_year.target_month
		mon_days = monthrange(target_year, target_mon)[1] 

		# for each day of target_year.target_month
		prev_avg_temp = []
		for tday in range(1, mon_days+1): 
			same_month = target_temp_data[target_temp_data['month']==target_mon] 
			target_day = same_month[same_month['date']==tday] 
			prev_avg_temp.append( [target_day['avgTemp'].values[0]] )

	else:
		print ("Wrong option for predict_temp()")
		# TODO: may require a proper error handling
		return

	# return predicted or true avgTemp
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
		num_of_sub: float, the predicted number of subscribers
	'''

	# return the predicted number of subscribers
	if sub_mode == 0:
		# load the insu and sub data of recent 4 years
		for tyear in range(target_year-4, target_year):
			# read the insu and sub ddata
			sub_data_tmp = pd.read_csv('data/sub/%s_sub_%d'%(area, tyear), delim_whitespace=True)
			# merge the read data into one data for easy processing
			if tyear == target_year-4:
				sub_data = sub_data_tmp	
			if tyear > target_year-4:
				sub_data = sub_data.append(sub_data_tmp)

		# extract sub data from the data of recent 4 years
		sub_num_list = []
		for tyear in range(target_year-4, target_year):
			prev_same_year = sub_data[sub_data['year']==tyear] 
			prev_same_month = prev_same_year[prev_same_year['month']==target_mon] 
			target_day = prev_same_month[prev_same_month['date']==1] 
			sub_num_list.append(target_day['sub_%s'%(cat)].values[0])

		# if all elements of sub_num_list are same, curve fitting is useless. In this case, return the data itself.
		if all(x == sub_num_list[0] for x in sub_num_list):
			return sub_num_list[0]
		# otherwise, conduct curve fitting.
		else:
			popt_a, popt_b = curve_fitting(range(1, len(sub_num_list)+1), sub_num_list)
			return popt_a * (len(sub_num_list)+1) + popt_b
	
	# return the true number of subscribers
	elif sub_mode == 1 :

		# load the true number of subscribers data
		sub_data = pd.read_csv('data/sub/%s_sub_%d'%(area, target_year), delim_whitespace=True)

		# extract the required data
		prev_same_month = sub_data[sub_data['month']==target_mon] 
		sub_num_data = prev_same_month['sub_%s'%(cat)].values[0]

		return sub_num_data

	else:
		print ("Wrong option for predict_sub_num()")
		# TODO: may require a proper error handling
		return


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


def predict_avg_insu_by_temp_regression(area, cat, target_year, target_mon, temp_mode):
	'''
	This function predicts avg insu per subscriber of a specified category through temp-based regression.
	Args:
		area: string, target area of prediction
		cat: string, target category of prediction
		target_year: int, the target year of prediction
		target_mon: int, the target month of prediction
		temp_mode: int, whether to use the predicted temp (0) or the true temp data (1)
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
		temp_data = pd.read_csv('data/temperature/%s_temp_%d'%(area, tyear), delim_whitespace=True)

		# read the insu data
		insu_data = pd.read_csv('data/insu/%s_insu_%d'%(area, tyear), delim_whitespace=True)

		# read the subscriber data
		sub_data = pd.read_csv('data/sub/%s_sub_%d'%(area, tyear), delim_whitespace=True)

		# read the date data
		date_data = pd.read_csv('data/date/date_info_Y%d'%(tyear), delim_whitespace=True)

		# extract data realted to mon_list
		for tmon in mon_list: 

			# extract temperature data of the target month
			temp_data_month = temp_data[temp_data['month']==tmon] 

			# extract date data of the target month
			date_data_month = date_data[date_data['month']==tmon] 

			# extract insu data of the target month
			insu_data_month = insu_data[insu_data['month']==tmon] 

			# extract sub data of the target month
			sub_data_month = sub_data[sub_data['month']==tmon] 
	
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
				train_data.append([avg_temp, dayCode, holidayCode])
			
				# prepare train LABEL
				# - calculate the average insu per sub
				insu_data_day = insu_data_month[insu_data_month['date']==tday] 
				insu_target = insu_data_day['insu_%s'%(cat)].values[0] 
				#
				sub_data_day = sub_data_month[sub_data_month['date']==tday] 
				sub_target = sub_data_day['sub_%s'%(cat)].values[0] 
				#
				train_label.append(insu_target/sub_target)

	# train a boosting model
	trained_model = train_boosting_model(train_data, train_label)
	
	# get the predicted temperature of the target_year.target_mon
	prev_avg_temp = predict_temp(area, target_year, target_mon, temp_mode)

	# get the date info of target_year.target_mon
	date_data = pd.read_csv('data/date/date_info_Y%d'%(target_year), delim_whitespace=True)

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
		target_date_list.append([dayCode, holidayCode])

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

	# load the insu and sub data of recent 3 years
	for tyear in range(target_year-3, target_year):

		# read the insu data
		insu_data_tmp = pd.read_csv('data/insu/%s_insu_%d'%(area, tyear), delim_whitespace=True)
		# - merge the read data into one data for easy processing
		if tyear == target_year-3:
			insu_data = insu_data_tmp	
		else:
			insu_data = insu_data.append(insu_data_tmp)

		# read the sub data
		sub_data_tmp = pd.read_csv('data/sub/%s_sub_%d'%(area, tyear), delim_whitespace=True)
		# - merge the read data into one data for easy processing
		if tyear == target_year-3:
			sub_data = sub_data_tmp	
		else:
			sub_data = sub_data.append(sub_data_tmp)

		# read the date data
		date_data_tmp = pd.read_csv('data/date/date_info_Y%d'%(tyear), delim_whitespace=True)
		# - merge the read data into one data for easy processing
		if tyear == target_year-3:
			date_data = date_data_tmp	
		else:
			date_data = date_data.append(date_data_tmp)

	# calculate the number of days of target_year.target_mon
	mon_days = monthrange(target_year, target_mon)[1] 
	
	# read the date data of the target_year
	target_date_data = pd.read_csv('data/date/date_info_Y%d'%(target_year), delim_whitespace=True)

	# for each day of target_year.target_mmon
	prev_avg_insu = []
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

				prev_same_year = insu_data[insu_data['year']== tyear]
				prev_same_month = prev_same_year[prev_same_year['month']==t_mon] 
				target_day = prev_same_month[prev_same_month['date']==t_date] 
				insu_target = target_day['insu_%s'%(cat)].values[0] 

				prev_same_year = sub_data[sub_data['year']== tyear]
				prev_same_month = prev_same_year[prev_same_year['month']==t_mon] 
				target_day = prev_same_month[prev_same_month['date']==t_date] 
				sub_target = target_day['sub_%s'%(cat)].values[0] 

				# get the average insu per sub	
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

		# load the insu data
		insu_data_tmp = pd.read_csv('data/insu/%s_insu_%d'%(area, tyear), delim_whitespace=True)
		# - merge the read data into one data for easy handling
		if tyear == target_year-3:
			insu_data = insu_data_tmp	
		else: 
			insu_data = insu_data.append(insu_data_tmp)

		# load the sub data
		sub_data_tmp = pd.read_csv('data/sub/%s_sub_%d'%(area, tyear), delim_whitespace=True)
		# - merge the read data into one data for easy handling
		if tyear == target_year-3:
			sub_data = sub_data_tmp	
		else:
			sub_data = sub_data.append(sub_data_tmp)
		
		# date data
		date_data_tmp = pd.read_csv('data/date/date_info_Y%d'%(tyear), delim_whitespace=True)
		# - merge the read data into one data for easy handling
		if tyear == target_year-3:
			date_data = date_data_tmp	
		else:
			date_data = date_data.append(date_data_tmp)

	# calculate the number of days of target_year.target_mon
	mon_days = monthrange(target_year, target_mon)[1] 

	# read the date data of the target_year
	target_date_data = pd.read_csv('data/date/date_info_Y%d'%(target_year), delim_whitespace=True)

	# for each day of target_year.target_mmon
	prev_avg_insu = []
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

				prev_same_year = insu_data[insu_data['year']== tyear]
				prev_same_month = prev_same_year[prev_same_year['month']==t_mon] 
				target_day = prev_same_month[prev_same_month['date']==t_date] 
				insu_target = target_day['insu_%s'%(cat)].values[0] 

				prev_same_year = sub_data[sub_data['year']== tyear]
				prev_same_month = prev_same_year[prev_same_year['month']==t_mon] 
				target_day = prev_same_month[prev_same_month['date']==t_date] 
				sub_target = target_day['sub_%s'%(cat)].values[0] 

				# get the average insu per sub	
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
		temp_mode: int, whether to use the predicted temp (0) or the ture temp data (1)
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
	
	if area == "naju":
		category = ['house', 'houseCooking', 'houseJHeating', 'salesOne', 'salesTwo', 'bizHeating', 'bizCooling', 'industry', 'heatFacility', 'heatCombined', 'CNG']

	else:
		print ("%s is not currely supported"%(area))
		return

	return category


def estimate_insu_per_cat(area, cat, target_year, target_month, temp_mode, sub_mode):
	'''
	This function estimates insu per category for target_year.target_month.
	Args:
		area: string, target area of prediction
		cat: string, a category to be predicted
		target_year: int, target year of prediction
		target_month: int, target month of prediction
		temp_mode: int, whether to use the predicted temp (0) or the true temp (1) data
		sub_mode: int, whether to use the predicted number of subscribers (0) or the true number of subscribers (1)
	Returns:
		daily_cat_pred_insu: list, a list of daily predictions for target_year.target_month
		true_insu_list: list, a list of daliy true insu data for target_year.target_month
	'''

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
		true_insu_data = pd.read_csv('data/insu/%s_insu_%d'%(area, target_year), delim_whitespace=True)
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


# load the file
import crawling_temp 
def gen_temp_file(area, target_year):
	'''
	This function generates a temperature file.
	Args:
		area: string, target area of prediction
		target_year: int, target year of prediction
	'''

	crawling_temp.crawling_main(area, target_year)


# load the file
import get_date_info
def gen_date_file(target_year):
	'''
	This function generates a datee file.
	Args:
		target_year: int, target year of prediction
	'''

	get_date_info.get_date_main(target_year)


import os
import re
def check_and_prepare_data(area, start_year, start_month, month_range, temp_mode, sub_mode):
	'''
	This function examines whether the required files exist or not.
	If required and possible, this function generates the required files.
	Args:
		area: string, target area of prediction
		start_year: int, start year of prediction
		start_month: int, start month of prediction
		month_range: int, the number of months to be predicted
		temp_mode: int, whether to use the predicted temp (0) or the true temp (1)
		sub_mode: int, whether to use the predicted number of subscribers (0) or the true number of subscribers (1)
	'''

	# exmine the availability of true insu and sub data
	
	# - exaimne available insu data files
	insu_file_list = os.listdir('data/insu')
	# - find the latest year of available insu data
	insu_year_list = []
	for insu_file in insu_file_list:
		insu_number = re.findall("\d+", insu_file)
		if len(insu_number) > 0 :
			insu_year_list.append(insu_number[0])
	insu_latest_year = int(max(insu_year_list))
	# find the latest month
	insu_latest_data = pd.read_csv('data/insu/%s_insu_%d'%(area, insu_latest_year), delim_whitespace=True)
	insu_latest_month = 0
	for tmon in range(1, 13):
		same_month = insu_latest_data[insu_latest_data['month']== tmon]
		if  len(same_month) > 0 :
			insu_latest_month = tmon

	# - examine available sub data files
	sub_file_list = os.listdir('data/sub')
	# - find the latest year of available sub data
	sub_year_list = []
	for sub_file in sub_file_list:
		sub_number = re.findall("\d+", sub_file)
		if len(sub_number) > 0 :
			sub_year_list.append(sub_number[0])
	sub_latest_year = int(max(sub_year_list))
	# find the latest month
	sub_latest_data = pd.read_csv('data/sub/%s_sub_%d'%(area, sub_latest_year), delim_whitespace=True)
	sub_latest_month = 0
	for tmon in range(1, 13):
		same_month = sub_latest_data[sub_latest_data['month']== tmon]
		if  len(same_month) > 0 :
			sub_latest_month = tmon

	if insu_latest_year < sub_latest_year:
		latest_year = insu_latest_year
		latest_month = insu_latest_month
	elif insu_latest_year > sub_latest_year:
		latest_year = sub_latest_year
		latest_month = sub_latest_month
	else:
		if insu_latest_month <= sub_latest_month:
			latest_month = insu_latest_month
		else:
			latest_month = sub_latest_month
		
	print (latest_year, latest_month)

	sys.exit()
	

	# generate a list of years to be considered
	year_list = []
	current = datetime.date(start_year, start_month, 1)
	current = current - datetime.timedelta(days=monthrange(current.year, current.month)[1])
	for ridx in range(1, month_range+1):
		current = current + datetime.timedelta(days=monthrange(current.year, current.month)[1])

		if not current.year in year_list:
			year_list.append(current.year)

	# for the years
	for current_year in year_list:

		# 1. temperature files
		# - the required files for predicting the temp
		for tyear in range(current_year-4, current_year):
			if not os.path.isfile('data/temperature/%s_temp_%d'%(area, tyear)):
				print ("The required file [./data/temperature/%s_temp_%d] does not exist"%(area, tyear))
				gen_temp_file(area, tyear)
				print ("The required file [./data/temperature/%s_temp_%d] is generated"%(area, tyear))
		# - only when the true temp data is required
		if temp_mode == 1:
			if not os.path.isfile('data/temperature/%s_temp_%d'%(area, current_year)):
				print ("The required file [./data/temperature/%s_temp_%d] does not exist"%(area, current_year))
				gen_temp_file(area, tyear)
				print ("The required file [./data/temperature/%s_temp_%d] is generated"%(area, current_year))

		# 2. insu files
		for tyear in range(current_year-4, current_year):
			if not os.path.isfile('data/insu/%s_insu_%d'%(area, tyear)):
				print ("The required file [./data/insu/%s_insu_%d] does not exist. This file should be prepared by HyGAS"%(area, tyear))
				return

		# 3. subscriber files
		for tyear in range(current_year-4, current_year):
			if not os.path.isfile('data/sub/%s_sub_%d'%(area, tyear)):
				print ("The required file [./data/sub/%s_sub_%d] does not exist. This file should be prepared by HyGAS"%(area, tyear))
				return
		# - only when the true sub num data is required
		if sub_mode == 1:
			if not os.path.isfile('data/sub/%s_sub_%d'%(area, current_year)):
				print ("The required file [./data/sub/%s_sub_%d] does not exist. This file should be prepared by HyGAS"%(area, current_year))
				return
	
		# 4. date files
		for tyear in range(current_year-4, current_year+1):
			if not os.path.isfile('data/date/date_info_Y%d'%(tyear)):
				print ("The required file [./data/date/date_info_Y%d] does not exist"%(tyear))
				gen_date_file(tyear)
				print ("The required file [./data/date/date_info_Y%d] is generated"%(tyear))


import math
import datetime
def conduct_predict_month(area, start_year, start_month, month_range, temp_mode, sub_mode):
	'''
	This function conducts prediction for 24 months.
	Args:
		area: string, target area of prediction
		start_year: int, start year of target prediction
		start_month: int, start month of target prediction
		month_range: int, the number of months to be predicted (e.g., prediction target => FROM start_year.start_month TO start_year.start_month + month_range)
		temp_mode: int, whether to use the predicted temp (0) or the true temp (1) data
		sub_mode: int, whether to use the predicted number of subscribers (0) or the true number of subscribers (1) data
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
	data += "pred_sum true_sum sum_mape\n"
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
		daily_true_insu_list = [] # a list of true insu of all categories of a target month. used for writing result into a file. 
		daily_pred_insu_list = [] # a list of predicted insu of all categories of a targer month. used for writing result into a file.

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


def conduct_predict_days(area, start_year, start_month, month_range, temp_mode, sub_mode):
	'''
	This function conducts prediction for 30days.
	Args:
		area: string, target area of prediction
		start_year: int, start year of target prediction
		start_month: int, start month of target prediction
		month_range: int, the number of months to be predicted (e.g., prediction target => FROM start_year.start_month TO start_year.start_month + month_range)
		temp_mode: int, whether to use the predicted temp (0) or the true temp (1) data
		sub_mode: int, whether to use the predicted number of subscribers (0) or the true number of subscribers (1) data
	'''

	# a list of categories relevant to target area
	category = get_category(area)

	# for each month from the start_year.start_month to start_year.start_month + month_range
	current = datetime.date(start_year, start_month, 1)
	current = current - datetime.timedelta(days=monthrange(current.year, current.month)[1])
	for ridx in range(1, month_range+1):

		current = current + datetime.timedelta(days=monthrange(current.year, current.month)[1])
		daily_pred_insu_list = [] # a list of predicted insu of all categories of a targer month. used for writing result into a file.

		# for each category
		for cat in category:

			# estimate daily insu per category
			est_insu, true_insu = estimate_insu_per_cat(area, cat, current.year, current.month, temp_mode, sub_mode)
			daily_pred_insu_list.append(est_insu)

		return np.mean(daily_pred_insu_list, axis=0)



# # # # # # # # # # # # # # # # # # # # # # # #
#                M a i n                      #
# # # # # # # # # # # # # # # # # # # # # # # #
import sys

def main(area, start_year, start_month, month_range, temp_mode, sub_mode, output_mode=2):
	'''
	This function mainly controls predictions.
	Args:
		area: string, target area of prediction
		start_year: int, start year of target prediction
		start_month: int, start month of target prediction
		month_range: int, the number of months to be predicted (e.g., prediction target => FROM start_year.start_month TO start_year.start_month + month_range)
		temp_mode: int, whether to use the predicted temp (0) or the true temp (1) data
		sub_mode: int, whether to use the predicted number of subscribers (0) or the true number of subscribers (1) data
		output_mode: int, whether to write the result into files (1) or return the prediction result to another file (2)	
	'''

	# Conduct predictions
	# - conduct predictions for 24 months and write the result to files
	if output_mode == 1:
		# Check whether the required files exist AND generate the required files if possible
		check_and_prepare_data(area, start_year, start_month, month_range, temp_mode, sub_mode)

		conduct_predict_month(area, start_year, start_month, month_range, temp_mode, sub_mode)

	# - conduct predictions for 1 months and return the result to other file. The returned results are used for prediction of 30days
	elif output_mode == 2:
		return conduct_predict_days(area, start_year, start_month, month_range, temp_mode, sub_mode)


if __name__ == "__main__":

	# Get the input parameters
	# - target area of prediction (e.g., naju, gwangju, ....)
	area = sys.argv[1] 
	# - start year of prediction (e.g., 2018)
	start_year = int(sys.argv[2])
	# - start month of start year of prediction (e.g., 1)
	start_month = int(sys.argv[3])
	# - the number of months to be predicted from start_year.start_month (e.g., 12 -> 12 months from 2018.1)
	month_range = int(sys.argv[4])
	# - use the predicted temp or the measured temp (for the purpose of verification)
	temp_mode = int(sys.argv[5])
	# - use the predicted subscriber number or the true numer (for the purpose of verification)
	sub_mode = int(sys.argv[6])

	main(area, start_year, start_month, month_range, temp_mode, sub_mode, output_mode=1)
