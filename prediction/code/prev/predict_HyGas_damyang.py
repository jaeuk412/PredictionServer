import pandas as pd
import numpy as np

# # # # # # # # # # # # # # # # # # # # # # # #
#              F u n c t i o n s              #
# # # # # # # # # # # # # # # # # # # # # # # #


from calendar import monthrange
def write_prediction_to_file(target_year, tmon, daily_pred_insu_list, daily_true_insu_list, category_list, mode):
	'''
	This function writes daily prediction result into file.
	Args:
		target_year: int, target year of prediction
		tmon: int, target month of prediction
		daily_pred_insu_list: np.array, daily predicted insu
		daily_true_insu_list: np.array, daily true insu
		category_list: list, a list of categories of prediction target
		mode: int, writing mode (1: write true insu together if any, 2:write prediction only)
	'''

	# open a file to write results
	f = open('daily_prediction_damyang_%d'%(target_year), 'a+')

	# calculate the number of days of target_year.target_month
	mon_days = monthrange(target_year, tmon)[1] 

	if mode == 1:
		# for each day
		for tday in range(1, mon_days+1): 
			data = "%d %d %d "%(target_year, tmon, tday)

			pred_insu_sum = 0
			true_insu_sum = 0
			for tidx in range(len(category_list)):
				data += "%.1f %.1f "%(daily_pred_insu_list[tidx][tday-1], daily_true_insu_list[tidx][tday-1])
				pred_insu_sum += daily_pred_insu_list[tidx][tday-1]
				true_insu_sum += daily_true_insu_list[tidx][tday-1]
			data += "%.1f %.1f\n"%(pred_insu_sum, true_insu_sum)

			f.write(data)

	elif mode == 2:
		# for each day
		for tday in range(1, mon_days+1): 
			data = "%d %d %d "%(target_year, tmon, tday)

			pred_insu_sum = 0
			for tidx in range(len(category_list)):
				data += "%.1f "%(daily_pred_insu_list[tidx][tday-1])
				pred_insu_sum += daily_pred_insu_list[tidx][tday-1]
			data += "%.1f\n"%(pred_insu_sum)

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

               
def predict_temp(raw_data, target_year, target_mon):
	'''
	This function estimates temperature of target_year.target_month by averaging the temperature of the same date of recent 4 years.
	Args:
		raw_data: pd.DataFrame, history data
		target_year: int, the target year of prediction
		target_mon: int, the target month of prediction
	Returns:
		prev_avg_temp: np.array, predicted daily temperature of target_year.target_mon
	'''

	# manipulate weight for averaging temp. note that winter of Y2017 and Y2018 was colder than normal
	if target_year == 2019 and target_mon in [1, 2]:
		weight_list = [1, 1, 1, 0.3]
	else:
		weight_list = [1, 1, 1, 1]

	prev_avg_temp = []

	# get the number of days of target_year.target_month
	mon_days = monthrange(target_year, target_mon)[1] 
	
	# for each day of target_year.target_month
	for tday in range(1, mon_days+1): 
		prev_avg_temp_list = []
		
		# for recent 4 years
		for tyear in range(target_year-4, target_year):
			prev_same_year = raw_data[raw_data['year']== tyear]
			prev_same_month = prev_same_year[prev_same_year['month']==target_mon] 
			target_day = prev_same_month[prev_same_month['date']==tday] 

			avg_temp = target_day['avgTemp'].values[0] 
			prev_avg_temp_list.append(avg_temp)

		# averaging 'avgTemp' of recent 4 years
		#prev_avg_temp.append( np.mean(prev_avg_temp_list) )
		prev_avg_temp.append( np.average(prev_avg_temp_list, weights=weight_list) )

	# return daily predicted avgTemp
	return np.array(prev_avg_temp)


def predict_sub_num(cat, raw_data, target_year, target_mon):
	'''
	This function estimates the number of subscribers of specified category of target_year.target_month by conducting curve fitting.
	Args:
		cat: string, target category of prediction
		raw_data: pd.DataFrame, history data
		target_year: int, the target year of prediction
		target_mon: int, the target month of prediction
	Returns:
		float, the predicted number of subscribers
	'''

	sub_num_list = []
	
	# for recent 4 years
	for tyear in range(target_year-4, target_year):
		prev_same_year = raw_data[raw_data['year']==tyear] 
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


def predict_avg_insu_by_temp_regression(cat, raw_data, target_year, target_mon):
	'''
	This function predicts avg insu per subscriber of a specified category through temp-based regression.
	Args:
		cat: string, target category of prediction
		raw_data: pd.DataFrame, history data
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

	train_avg_temp_list = [] # input list of curve fitting. 'x' of 'y=a*x+b'
	train_avg_insu_target = [] # output list of curve fittng. 'y' of 'y=a*x+b'

	# for recent 4 years
	for tyear in range(target_year-4, target_year):

		prev_same_year = raw_data[raw_data['year']==tyear] 

		# for relevant months
		for tmon in mon_list: 

			prev_same_month = prev_same_year[prev_same_year['month']==tmon] 
	
			# calculate the number of days of tyear.tmon
			mon_days = monthrange(tyear, tmon)[1] 

			# for each day of tyear.tmon
			for tday in range(1, mon_days+1): 
				target_day = prev_same_month[prev_same_month['date']==tday] 

				# get 'avgTemp' [to be used as input for curve fitting]
				avg_temp = target_day['avgTemp'].values[0]
				train_avg_temp_list.append(avg_temp)
			
				# calculate the average insu per sub [to be used as output for curve fitting]
				insu_target = target_day['insu_%s'%(cat)].values[0] 
				sub_target = target_day['sub_%s'%(cat)].values[0] 
				train_avg_insu_target.append(insu_target/sub_target)

	# conduct temp-based curve fitting with training data and get 'a' and 'b' of 'y=a*x + b'
	popt_a, popt_b = curve_fitting(train_avg_temp_list, train_avg_insu_target)
	
	# get the predicted temperature of the target_year.target_mon
	prev_avg_temp = predict_temp(raw_data, target_year, target_mon)

	# apply 'a' and 'b' for the predicted temperature to estimate the average insu per sub
	pred_avg_insu = popt_a * np.array(prev_avg_temp) + popt_b

	return pred_avg_insu


def predict_avg_insu_by_averaging(cat, raw_data, target_year, target_mon):
	'''
	This function predicts avg insu per sub by averaging data of recent 3 years
	Args:
		cat: string, target category of prediction
		raw_data: pd.DataFrame, history data
		target_year: int, the target year of prediction
		target_mon: int, the target month of prediction
	Returns:
		pred_avg_insu: np.array, the predicted daily average insu per subscriber
	'''

	prev_avg_insu = []

	# calculate the number of days of target_year.target_mon
	mon_days = monthrange(target_year, target_mon)[1] 

	# for each day of target_year.target_mmon
	for tday in range(1, mon_days+1): 

		# handle special case (i.e., 29 Feb)
		if target_mon == 2 and tday == 29:
			tday = 28

		prev_avg_insu_target = []

		# for recent 3 years
		for tyear in range(target_year-3, target_year):
			prev_same_year = raw_data[raw_data['year']== tyear]
			prev_same_month = prev_same_year[prev_same_year['month']==target_mon] 
			target_day = prev_same_month[prev_same_month['date']==tday] 

			# get the average insu per sub	
			insu_target = target_day['insu_%s'%(cat)].values[0] 
			sub_target = target_day['sub_%s'%(cat)].values[0] 
			prev_avg_insu_target.append(insu_target/sub_target)

		# delete useless data
		prev_avg_insu_target = np.array(prev_avg_insu_target)
		prev_avg_insu_target = prev_avg_insu_target[prev_avg_insu_target != 0.]

		# if 'prev_avg_insu_target' includes data, use the average
		if len(prev_avg_insu_target) > 0:
			prev_avg_insu.append( np.average(prev_avg_insu_target))
		# otherwise, use 0
		else:
			prev_avg_insu.append(0)

	return np.array(prev_avg_insu)


def predict_avg_insu_by_curve_fitting(cat, raw_data, target_year, target_mon):
	'''
	This function predicts avg insu per sub by conducting curve fitting with data of recent 3 years
	Args:
		cat: string, target category of prediction
		raw_data: pd.DataFrame, history data
		target_year: int, the target year of prediction
		target_mon: int, the target month of prediction
	Returns:
		pred_avg_insu: np.array, the predicted daily average insu per subscriber
	'''

	# calculate the number of days of target_year.target_mon
	mon_days = monthrange(target_year, target_mon)[1] 

	prev_avg_insu = []
	# for each day of target_year.target_mmon
	for tday in range(1, mon_days+1): 

		# handle special case (i.e., 29 Feb)
		if target_mon == 2 and tday == 29:
			tday = 28

		prev_avg_insu_target = []
		# for recent 3 years
		for tyear in range(target_year-3, target_year):
			prev_same_year = raw_data[raw_data['year']== tyear]
			prev_same_month = prev_same_year[prev_same_year['month']==target_mon] 
			target_day = prev_same_month[prev_same_month['date']==tday] 

			# get the average insu per sub	
			insu_target = target_day['insu_%s'%(cat)].values[0] 
			sub_target = target_day['sub_%s'%(cat)].values[0] 
			prev_avg_insu_target.append(insu_target/sub_target) 

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


def predict_avg_insu(cat, raw_data, target_year, target_mon):
	'''
	This function estimates the average insu per subscriber of specified category of target_year.target_month through temmp-based linear regression.
	This function applies different prediction methods for target categories.
	Args:
		cat: string, target category of prediction
		raw_data: pd.DataFrame, history data
		target_year: int, the target year of prediction
		target_mon: int, the target month of prediction
	Returns:
		pred_avg_insu: np.array, the predicted daily average insu per subscriber
	'''

	# temp-based linear regression (i.e., input: temp, output: avg insu per sub)
	if cat in ['house', 'houseJHeating']:

		return predict_avg_insu_by_temp_regression(cat, raw_data, target_year, target_mon)

	# averaging data of recent 3 years
	elif cat in ['salesOne', 'salesTwo', 'bizHeating', 'bizCooling', 'industry']:

		return predict_avg_insu_by_averaging(cat, raw_data, target_year, target_mon)

	# curve fitting. 'CNG'
	else:
		return predict_avg_insu_by_curve_fitting(cat, raw_data, target_year, target_mon)


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

	monthly_diff = monthly_label_sum - monthly_pred_sum

	return daily_mape, monthly_mape, monthly_diff


import math
def conduct_predict(history_file_name, target_year):
	'''
	This function conducts prediction.
	Args:
		history_file_name: string, file name of history data
		target_year: int, year of target prediction
	Returns:
		None.
	'''

	# read the previous history
	raw_data = pd.read_csv(history_file_name, delim_whitespace=True)

	# a list of categories relevant to Naju area
	damyang_category = ['house', 'houseJHeating', 'salesOne', 'salesTwo', 'bizHeating', 'bizCooling', 'industry']

	# to see if there exist true data of target_year
	tmp_year = raw_data[raw_data['year']== target_year]
	tmp_cat = np.array(tmp_year['insu_house'])

	# when there exit true label of target_year (e.g., 2018)
	if math.isnan(float(tmp_cat[0])) == False:

		# prepare prediciton output file
		f = open('daily_prediction_damyang_%s'%(target_year), 'w')
		# - write column name first
		data = "year month date "
		for tidx in range(len(damyang_category)):
			data += "%s_pred %s_true "%(damyang_category[tidx], damyang_category[tidx])
		data += "pred_sum true_sum\n"
		f.write(data)
		f.close()

		month_mape_list = [] # a list of monthly mape. used to calculate average monthly mape
		yearly_pred_sum = 0 # yearly sum of daily predicted insu of target year. used to calculcate yearly mape
		yearly_true_sum = 0 # yearly sum of daily true insu of target year. used to calculate yearly mape

		# for 12 months of the target year
		for tmon in range(1,13):

			print ("%d : "%(tmon), end='')

			monthly_pred_sum = 0 # monthly sum of daily predicted insu of target_year.tmon. used to calculate monthly mape
			monthly_true_sum = 0 # monthly sum of daily true insu of target_year.tmon. used to calculate monthly mape

			daily_true_insu_list = [] # a list of true insu of all category of a target month. used for writing result into a file.
			daily_pred_insu_list = [] # a list of predicted insu of all category of a targer month. used for writing result into a file.

			# for each category
			for cat in damyang_category:

				# get the predicted avg insu per sub
				pred_avg_insu = predict_avg_insu(cat, raw_data, target_year, tmon)

				# get the predicted subscriber number
				pred_sub_num = math.ceil(predict_sub_num(cat, raw_data, target_year, tmon))

				# estimate insu volume of target month. 'daily_cat_pred_insu' contains daily predicted insu
				daily_cat_pred_insu = pred_avg_insu * pred_sub_num

				# store for calculating prediction errors
				daily_pred_insu_list.append(daily_cat_pred_insu)
				monthly_pred_sum += np.sum(daily_cat_pred_insu)

				# get true insu volume of target month. 'daily_cat_true_insu' contains daily true insu
				daily_cat_true_insu = []
				prev_same_year = raw_data[raw_data['year']== target_year]
				prev_same_month = prev_same_year[prev_same_year['month']==tmon] 
				mon_days = monthrange(target_year, tmon)[1] 
				for tday in range(1, mon_days+1): 
					target_day = prev_same_month[prev_same_month['date']==tday] 
					daily_cat_true_insu.append(target_day['insu_%s'%(cat)].values[0])
				daily_cat_true_insu = np.array(daily_cat_true_insu)

				# store for calculating prediction errors
				daily_true_insu_list.append(daily_cat_true_insu)
				monthly_true_sum += np.sum(daily_cat_true_insu)

				# calculate prediction errors
				cat_daily_mape, cat_monthly_mape, cat_monthly_diff = calc_errors(daily_cat_true_insu, daily_cat_pred_insu)
				print ("%.3f %.3f %.3f, "%(cat_monthly_diff, cat_daily_mape, cat_monthly_mape), end='')

			# write prediction result into file
			write_prediction_to_file(target_year, tmon, daily_pred_insu_list, daily_true_insu_list, damyang_category, 1)

			# daily prediction and true insu (sum of all categories) data. used to calculate monthly mape
			daily_pred_insu_list = np.mean(daily_pred_insu_list, axis=0)
			daily_true_insu_list = np.mean(daily_true_insu_list, axis=0)

			# store for calculating prediction errors
			yearly_pred_sum += monthly_pred_sum
			yearly_true_sum += monthly_true_sum

			# average of monthly prediction errors
			print ("%.3f %.3f %.3f"%(monthly_true_sum - monthly_pred_sum, np.mean(abs(daily_true_insu_list-daily_pred_insu_list)*100/daily_true_insu_list), abs(monthly_true_sum - monthly_pred_sum)*100/monthly_true_sum))
			month_mape_list.append(abs(monthly_true_sum - monthly_pred_sum)*100/monthly_true_sum)

		# yearly prediction error
		print ("%.3f %.3f"%(np.mean(month_mape_list), np.std(month_mape_list)))
		print ("%.3f"%( abs(yearly_true_sum - yearly_pred_sum)*100/yearly_true_sum))

	# when there is no true label of target_year (e.g., 2019)
	else:
		# prepare prediciton output file
		f = open('daily_prediction_damyang_%s'%(target_year), 'w')
		# write column name first
		data = "year month date "
		for tidx in range(len(damyang_category)):
			data += "%s "%(damyang_category[tidx])
		data += "pred_sum\n"
		f.write(data)
		f.close()

		# true monthly insu volume of Y2019 of damyang area
		true_insu_monthly = [8598413, 7078181, 7189584, 5575657, 5639429, 4892209]
		month_mape_list = []
		yearly_pred_sum = 0
		for tmon in range(1,7):

			print ("%d : "%(tmon), end='')

			monthly_pred_sum = 0
			daily_pred_insu_list = []
			for cat in damyang_category:
				# get the predicted avg insu per sub
				pred_avg_insu = predict_avg_insu(cat, raw_data, target_year, tmon)

				# get the predicted subscriber number
				pred_sub_num = math.ceil(predict_sub_num(cat, raw_data, target_year, tmon))

				# estimate monthly insu volume. 'daily_cat_pred_insu' contains daily predicted insu
				daily_cat_pred_insu = pred_avg_insu * pred_sub_num
				daily_pred_insu_list.append(daily_cat_pred_insu)

				# store for calculating prediction errors
				monthly_pred_sum += np.sum(daily_cat_pred_insu)

				print ("%.3f, "%(np.sum(daily_cat_pred_insu)), end='')

			# write prediction result into file
			write_prediction_to_file(target_year, tmon, daily_pred_insu_list, daily_pred_insu_list, damyang_category, 2)

			# monthly prediction errors
			yearly_pred_sum += monthly_pred_sum
			print ("%.3f %.3f"%(true_insu_monthly[tmon-1]-monthly_pred_sum, abs(true_insu_monthly[tmon-1] - monthly_pred_sum)*100/true_insu_monthly[tmon-1]))
			month_mape_list.append(abs(true_insu_monthly[tmon-1] - monthly_pred_sum)*100/true_insu_monthly[tmon-1])

		# yearly prediction error
		print ("%.3f %.3f"%(np.mean(month_mape_list), np.std(month_mape_list)))
		print ("%.3f"%(abs(np.sum(true_insu_monthly)-yearly_pred_sum)*100/np.sum(true_insu_monthly)))
		

# # # # # # # # # # # # # # # # # # # # # # # #
#                M a i n                      #
# # # # # # # # # # # # # # # # # # # # # # # #

# predict daily insu of damyang of Y2018
conduct_predict('merged_damyang_2014_2018', 2018)
