import pandas as pd
import numpy as np
import prediction.predict_common as predict_common
from API.api_helper.user_directory import folder_path

# # # # # # # # # # # # # # # # # # # # # # # #
#              F u n c t i o n s              #
# # # # # # # # # # # # # # # # # # # # # # # #

from calendar import monthrange
def write_prediction_to_file(daily_output_file, target_year, tmon, daily_pred_insu_list, category_list):
	'''
	This function writes daily prediction result into file.
	Args:
		daily_output_file: string, output file name
		target_year: int, target year of prediction
		tmon: int, target month of prediction
		daily_pred_insu_list: np.array, daily predicted insu
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
		# prediction result of each category
		for tidx in range(len(category_list)):
			data += "%.1f "%(daily_pred_insu_list[tidx][tday-1])
			pred_insu_sum += daily_pred_insu_list[tidx][tday-1]

		data += "%.1f\n"%(pred_insu_sum)

		# write the result to the file
		f.write(data)

	f.close()


               
import os
def predict_temp(area, target_year, target_mon, target_day):
	'''
	This function estimates temperature of target_year.target_month by averaging the temperature of the same date of recent 4 years.
	Args:
		area: string, target area of prediction
		target_year: int, the target year of prediction
		target_mon: int, the target month of prediction
	Returns:
		prev_avg_temp: np.array, predicted daily temperature of target_year.target_mon
	'''

	# load the temperature data of recent 4 years
	for tyear in range(target_year-4, target_year):

		# read the temp data
		temp_data_tmp = pd.read_csv(folder_path+'data/temp/%s_temp_%d'%(area, tyear), delim_whitespace=True)
		# merge the read data into one data for easy processing
		if tyear == target_year-4:
			temp_data = temp_data_tmp	
		else:
			temp_data = temp_data.append(temp_data_tmp)


	prev_avg_temp = []
	target = datetime.date(target_year, target_mon, target_day)
	for tday in range(1, 31): 
		if target.month == 2 and target.day == 29: 
			t_day = 28
		else:
			t_day = target.day
	
		prev_avg_temp_list = []
		for tyear in range(target_year-4, target_year):
			prev_same_year = temp_data[temp_data['year']== tyear]
			prev_same_month = prev_same_year[prev_same_year['month']==target.month] 
			target_day_data = prev_same_month[prev_same_month['date']==t_day] 

			avg_temp = target_day_data['avgTemp'].values[0] 
			prev_avg_temp_list.append(avg_temp)

		# averaging 'avgTemp' of recent 4 years
		avg_over_years = np.mean(prev_avg_temp_list)
		prev_avg_temp.append( [avg_over_years] )

		target = target + datetime.timedelta(days=1)

	# return predicted or true avgTemp
	return np.array(prev_avg_temp)




def predict_sub_num(area, cat, target_year, target_mon, target_day):
	'''
	This function estimates the number of subscribers of specified category of target_year.target_month by conducting curve fitting.
	Args:
		area: string, target area of prediction
		cat: string, target category of prediction
		target_year: int, the target year of prediction
		target_mon: int, the target month of prediction
	Returns:
		num_of_sub: float, the predicted number of subscribers
	'''

	# load the insu and sub data of recent 4 years
	for tyear in range(target_year-4, target_year):
		# read the insu and sub ddata
		sub_data_tmp = pd.read_csv(folder_path+'data/sub/%s_sub_%d'%(area, tyear), delim_whitespace=True)
		# merge the read data into one data for easy processing
		if tyear == target_year-4:
			sub_data = sub_data_tmp	
		else:
			sub_data = sub_data.append(sub_data_tmp)

	sub_pred_list = []
	target = datetime.date(target_year, target_mon, target_day)
	for tday in range(1, 31): 
		if target.month == 2 and target.day == 29: 
			t_day = 28
		else:
			t_day = target.day
	
		# extract sub data from the data of recent 4 years
		sub_num_list = []
		for tyear in range(target_year-4, target_year):
			prev_same_year = sub_data[sub_data['year']==tyear] 
			prev_same_month = prev_same_year[prev_same_year['month']==target.month] 
			target_day_data = prev_same_month[prev_same_month['date']==t_day] 
			sub_num_list.append(target_day_data['sub_%s'%(cat)].values[0])

		# if all elements of sub_num_list are same, curve fitting is useless. In this case, return the data itself.
		if all(x == sub_num_list[0] for x in sub_num_list):
			pred_sub_tmp = sub_num_list[0]
		# otherwise, conduct curve fitting.
		else:
			popt_a, popt_b = predict_common.curve_fitting(range(1, len(sub_num_list)+1), sub_num_list)
			pred_sub_tmp = popt_a * (len(sub_num_list)+1) + popt_b

		sub_pred_list.append(math.ceil(pred_sub_tmp))

		target = target + datetime.timedelta(days=1)
	
	return sub_pred_list


def predict_avg_insu_by_temp_regression(area, cat, target_year, target_mon, target_day):
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
	for tyear in range(target_year-4, target_year+1):

		if not os.path.isfile(folder_path+'data/insu/%s_insu_%d'%(area, tyear)):
			continue

		# read the temperature data
		temp_data = pd.read_csv(folder_path+'data/temp/%s_temp_%d'%(area, tyear), delim_whitespace=True)

		# read the insu data
		insu_data = pd.read_csv(folder_path+'data/insu/%s_insu_%d'%(area, tyear), delim_whitespace=True)

		# read the subscriber data
		sub_data = pd.read_csv(folder_path+'data/sub/%s_sub_%d'%(area, tyear), delim_whitespace=True)

		# read the date data
		date_data = pd.read_csv(folder_path+'data/date/date_info_Y%d'%(tyear), delim_whitespace=True)

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
				# print("temp_data_day: ",temp_data_day)
				avg_temp = temp_data_day['avgTemp'].values[0]
				# print("avg_temp: ",avg_temp)
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
				# print(insu_target)
				#
				sub_data_day = sub_data_month[sub_data_month['date']==tday] 
				sub_target = sub_data_day['sub_%s'%(cat)].values[0] 
				#
				train_label.append(insu_target/sub_target)

	# train a boosting model
	trained_model = predict_common.train_boosting_model(train_data, train_label)
	
	# get the predicted temperature of the target_year.target_mon
	prev_avg_temp = predict_temp(area, target_year, target_mon, target_day)


	# get the date info of target_year.target_mon
	date_data = pd.read_csv(folder_path+'data/date/date_info_Y%d'%(target_year), delim_whitespace=True)

	target = datetime.date(target_year, target_mon, target_day)
	target_date_list = []
	for tday in range(1, 31): 
		if target.month == 2 and target.day == 29: 
			t_day = 28
		else:
			t_day = target.day
	
		same_month = date_data[date_data['month']== target.month] 
		same_date = same_month[same_month['date']==t_day] 
		dayCode = same_date['day'].values[0]
		holidayCode = same_date['holiday'].values[0]
		target_date_list.append([dayCode, holidayCode])

		target = target + datetime.timedelta(days=1)

	# generate test data
	test_data = np.hstack([prev_avg_temp, target_date_list])

	# conduct prediction
	pred_avg_insu = trained_model.predict(test_data)

	return pred_avg_insu



def predict_avg_insu_by_averaging(area, cat, target_year, target_mon, target_day):
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
		insu_data_tmp = pd.read_csv(folder_path+'data/insu/%s_insu_%d'%(area, tyear), delim_whitespace=True)
		# - merge the read data into one data for easy processing
		if tyear == target_year-3:
			insu_data = insu_data_tmp	
		else:
			insu_data = insu_data.append(insu_data_tmp)

		# read the sub data
		sub_data_tmp = pd.read_csv(folder_path+'data/sub/%s_sub_%d'%(area, tyear), delim_whitespace=True)
		# - merge the read data into one data for easy processing
		if tyear == target_year-3:
			sub_data = sub_data_tmp	
		else:
			sub_data = sub_data.append(sub_data_tmp)

		# read the date data
		date_data_tmp = pd.read_csv(folder_path+'data/date/date_info_Y%d'%(tyear), delim_whitespace=True)
		# - merge the read data into one data for easy processing
		if tyear == target_year-3:
			date_data = date_data_tmp	
		else:
			date_data = date_data.append(date_data_tmp)


	# calculate the number of days of target_year.target_mon
	mon_days = monthrange(target_year, target_mon)[1] 
	
	# read the date data of the target_year
	target_date_data = pd.read_csv(folder_path+'data/date/date_info_Y%d'%(target_year), delim_whitespace=True)

	prev_avg_insu = []
	target = datetime.date(target_year, target_mon, target_day)
	for tday in range(1, 31): 

		if target.month == 2 and target.day == 29: 
			t_day = 28
		else:
			t_day = target.day

		same_month = target_date_data[target_date_data['month']==target.month] 
		target_day_data = same_month[same_month['date']==t_day] 
		c_holiday = target_day_data['holiday'].values[0]
		c_day = target_day_data['day'].values[0]

		prev_avg_insu_target = []

		# for recent 3 years
		for tyear in range(target_year-3, target_year):

			# Fine relevant dates
			# - Find the index of the same date in previous years 
			same_year = date_data[date_data['year']==tyear] 
			same_month = same_year[same_year['month']==target.month] 
			same_date = same_month[same_month['date']==t_day] 
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

		target = target + datetime.timedelta(days=1)

	return np.array(prev_avg_insu)



def predict_avg_insu_by_curve_fitting(area, cat, target_year, target_mon, target_day):
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
		insu_data_tmp = pd.read_csv(folder_path+'data/insu/%s_insu_%d'%(area, tyear), delim_whitespace=True)
		# - merge the read data into one data for easy handling
		if tyear == target_year-3:
			insu_data = insu_data_tmp	
		else: 
			insu_data = insu_data.append(insu_data_tmp)

		# load the sub data
		sub_data_tmp = pd.read_csv(folder_path+'data/sub/%s_sub_%d'%(area, tyear), delim_whitespace=True)
		# - merge the read data into one data for easy handling
		if tyear == target_year-3:
			sub_data = sub_data_tmp	
		else:
			sub_data = sub_data.append(sub_data_tmp)
		
		# date data
		date_data_tmp = pd.read_csv(folder_path+'data/date/date_info_Y%d'%(tyear), delim_whitespace=True)
		# - merge the read data into one data for easy handling
		if tyear == target_year-3:
			date_data = date_data_tmp	
		else:
			date_data = date_data.append(date_data_tmp)

	# calculate the number of days of target_year.target_mon
	mon_days = monthrange(target_year, target_mon)[1] 

	# read the date data of the target_year
	target_date_data = pd.read_csv(folder_path+'data/date/date_info_Y%d'%(target_year), delim_whitespace=True)

	prev_avg_insu = []
	target = datetime.date(target_year, target_mon, target_day)
	for tday in range(1, 31): 

		if target.month == 2 and target.day == 29: 
			t_day = 28
		else:
			t_day = target.day

		same_month = target_date_data[target_date_data['month']==target.month] 
		target_day = same_month[same_month['date']==t_day] 
		c_holiday = target_day['holiday'].values[0]
		c_day = target_day['day'].values[0]

		prev_avg_insu_target = []

		# for recent 3 years
		for tyear in range(target_year-3, target_year):

			# Fine relevant dates
			# - Find the index of the same date in previous years 
			same_year = date_data[date_data['year']==tyear] 
			same_month = same_year[same_year['month']==target.month] 
			same_date = same_month[same_month['date']==t_day] 
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
			popt_a, popt_b = predict_common.curve_fitting(range(1, len(prev_avg_insu_target)+1), prev_avg_insu_target)
			prev_avg_insu.append(popt_a * (len(prev_avg_insu_target)+1) + popt_b)
		# if 'prev_avg_insu_target' contains only one data, use that data
		elif len(prev_avg_insu_target) == 1:
			prev_avg_insu.append(prev_avg_insu_target[0])
		# otherwise, use 0
		else:
			prev_avg_insu.append(0)

		target = target + datetime.timedelta(days=1)

	return np.array(prev_avg_insu)



def predict_avg_insu(area, cat, target_year, target_mon, target_day):
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

		return predict_avg_insu_by_temp_regression(area, cat, target_year, target_mon, target_day)

	# averaging data of recent 3 years
	elif cat in ['houseCooking', 'salesOne', 'bizHeating', 'bizCooling', 'heatFacility', 'heatCombined']:

		return predict_avg_insu_by_averaging(area, cat, target_year, target_mon, target_day)

	# curve fitting. 'CNG'
	else:
		return predict_avg_insu_by_curve_fitting(area, cat, target_year, target_mon, target_day)



def estimate_insu_per_cat(area, cat, target_year, target_month, target_day):
	'''
	This function estimates insu per category for target_year.target_month.
	Args:
		area: string, target area of prediction
		cat: string, a category to be predicted
		target_year: int, target year of prediction
		target_month: int, target month of prediction
	Returns:
		daily_cat_pred_insu: list, a list of daily predictions for target_year.target_month
		true_insu_list: list, a list of daliy true insu data for target_year.target_month
	'''

	# Estimate daily insu per category
	# - get the predicted avg insu per sub
	pred_avg_insu = predict_avg_insu(area, cat, target_year, target_month, target_day)

	# - get the predicted subscriber number
	pred_sub_num = predict_sub_num(area, cat, target_year, target_month, target_day)

	# - estimate insu volume of target month. 'daily_cat_pred_insu' contains daily predicted insu
	daily_cat_pred_insu = pred_avg_insu * pred_sub_num

	return daily_cat_pred_insu


	
import math
import datetime
def conduct_prediction(area, target_year, target_month, target_day):

	category = predict_common.get_category(area)

	daily_pred_insu_list = [] # a list of predicted insu of all categories of a targer month. used for writing result into a file.


	for cat in category:
		est_insu = estimate_insu_per_cat(area, cat, target_year, target_month, target_day)
		daily_pred_insu_list.append(est_insu)

	pred_list = []
	for tday in range(len(est_insu)):
		pred_insu_sum = 0
		for tidx in range(len(category)):
			pred_insu_sum += daily_pred_insu_list[tidx][tday]
		pred_list.append(pred_insu_sum)


	print(len(pred_list))
	return pred_list
# [275380.7136224828, 279551.956682468, 268314.91175310477, 273392.64062681136, 283776.52507027733, 268752.49494669266, 273643.5965949161, 273674.9457046605, 280983.1557769199, 265023.28407828714, 272569.07665904006, 274370.5516351158, 269762.2245988773, 269026.25900285895, 266737.65193983354, 267638.163720156, 256818.9021543437, 261076.98133872828, 264466.46256432345, 267973.91323309165, 265417.93349513866, 263341.38619928894, 259390.60788856272, 255533.8489797609, 249663.01151045325, 264826.75717203977, 263940.9541481543, 261518.75409955622, 257702.93183534755, 257181.44097216323]
# [263786.1401730134, 260154.38236195303, 262474.96827003744, 249310.56541298312, 231697.97952440684, 260093.5106644737, 260028.76573976947, 275282.88493135484, 267972.3974175139, 280586.3348293712, 273392.79001318145, 258991.34057806616, 277412.90311710245, 271644.19421150454, 283724.0616599313, 269292.61581159005, 268420.29631111573, 270452.8888521576, 274057.0445683076, 278820.19676042127, 275903.87805032096, 291610.67949239246, 284628.4602503103, 285388.16066253505, 276868.62961274106, 269123.78326826234, 284713.3425922396, 280611.21940367384, 294476.60654064687, 283467.1828450371]
# [275744.26555497403, 278822.9651710255, 267342.29006305465, 273222.3998975395, 283768.7263502023, 269954.628434986, 274584.17025839415, 274818.47110188234, 279424.5047114616, 264543.97312243225, 271246.73101358174, 274057.49440590164, 269487.99628800317, 268972.3935822241, 266600.84934450773, 267913.699795552, 257327.17040263367, 260984.71687244764, 265247.0191217374, 267391.23999064876, 265341.36819606397, 263204.5836039632, 260625.03874269724, 255355.58062712842, 251288.4288557871, 264440.26160164096, 264066.96576311265, 261327.14388703884, 257710.16921847523, 257540.06128494104]
## 나주 , 2019, 6월 , 30일동안(고정).
# print(conduct_prediction('naju', 2019, 6, 30))
