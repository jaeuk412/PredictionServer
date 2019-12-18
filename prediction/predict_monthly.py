import pandas as pd
import numpy as np
from API.api_helper.user_directory import folder_prediction_path

import os
import re
import datetime
import prediction.predict_common as predict_common
from calendar import monthrange


# area, op_mode, temp_mode, sub_mode
set_area = str
set_op_mode = int
set_temp_mode = int
set_sub_mode = int

def check_and_prepare_data(area, op_mode, temp_mode, sub_mode):
	'''
	This function examines whether the required files exist or not.
	If required and possible, this function generates the required files.
	Args:
		area: string, target area of prediction
		op_mode: int, examine prediction accuracy using the latest 1-year data (1) or conduct predictions for coming 24 months (2)
		temp_mode: int, whether to use the predicted temp (0) or the true temp (1)
		sub_mode: int, whether to use the predicted number of subscribers (0) or the true number of subscribers (1)
	'''

	# step 1: exmine the availability of true insu and sub data
	# - note that four data files are used -> insu, sub (the number of subscribers), temp (temp), and date (day, holiday info) files
	
	# step 1-1: exaimne available insu data files
	insu_file_list = os.listdir('data/insu')
	# - find the latest year of available insu data
	insu_year_list = []
	for insu_file in insu_file_list:
		insu_number = re.findall("\d+", insu_file)
		if len(insu_number) > 0 :
			insu_year_list.append(insu_number[0])
	insu_latest_year = int(max(insu_year_list))
	# - find the latest month of insu data
	insu_latest_data = pd.read_csv(folder_prediction_path + 'data/insu/%s_insu_%d' % (area, insu_latest_year), delim_whitespace=True)
	insu_latest_month = 0
	for tmon in range(1, 13):
		same_month = insu_latest_data[insu_latest_data['month']== tmon]
		if  len(same_month) > 0 :
			insu_latest_month = tmon

	# step 1-2: examine available sub data files
	sub_file_list = os.listdir('data/sub')
	# - find the latest year of available sub data
	sub_year_list = []
	for sub_file in sub_file_list:
		sub_number = re.findall("\d+", sub_file)
		if len(sub_number) > 0 :
			sub_year_list.append(sub_number[0])
	sub_latest_year = int(max(sub_year_list))
	# - find the latest month of sub data
	sub_latest_data = pd.read_csv(folder_prediction_path + 'data/sub/%s_sub_%d' % (area, sub_latest_year), delim_whitespace=True)
	sub_latest_month = 0
	for tmon in range(1, 13):
		same_month = sub_latest_data[sub_latest_data['month']== tmon]
		if  len(same_month) > 0 :
			sub_latest_month = tmon

	# step 1-2: find the latest year and latest month of both insu and sub data
	latest_year = 0
	latest_month = 0
	if insu_latest_year < sub_latest_year:
		latest_year = insu_latest_year
		latest_month = insu_latest_month
	elif insu_latest_year > sub_latest_year:
		latest_year = sub_latest_year
		latest_month = sub_latest_month
	else:
		latest_year = insu_latest_year
		if insu_latest_month <= sub_latest_month:
			latest_month = insu_latest_month
		else:
			latest_month = sub_latest_month

	print ("Both insu (%d.%d) and sub (%d.%d) data are available up to %d.%d"%(insu_latest_year, insu_latest_month, sub_latest_year, sub_latest_month, latest_year, latest_month))
		
	
	# step 2: examine the availability of other related files and prepare the files if required and possible for corresponding op_mode

	# step 2-1: conduct processes for op_mode of 1
	if op_mode == 1 :
		# - check temp files. the required files include the data of recent 4 years (input for prediction of latest_year) and the data of latest_year (predictio target. we need this to calculate prediction accuracy)
		for tyear in range(latest_year-4, latest_year+1):
			if not os.path.isfile(folder_prediction_path + 'data/temp/%s_temp_%d' % (area, tyear)):
				print ("The required file [./data/temp/%s_temp_%d] does not exist"%(area, tyear))
				predict_common.gen_temp_file(area, tyear)
				print ("The required file [./data/temp/%s_temp_%d] is generated"%(area, tyear))

		# - check date files
		for tyear in range(latest_year-4, latest_year+1):
			if not os.path.isfile(folder_prediction_path + 'data/date/date_info_Y%d' % (tyear)):
				print ("The required file [./data/date/date_info_Y%d] does not exist"%(tyear))
				predict_common.gen_date_file(tyear)
				print ("The required file [./data/date/date_info_Y%d] is generated"%(tyear))

		# - calculate start_year, start_month, and month_range to be used for further predictions
		target = datetime.date(latest_year, latest_month, monthrange(latest_year, latest_month)[1]) 
		target = target - datetime.timedelta(days=360)
		print ("Conduct prediction from %d.%d to %d.%d for the purpose of analysis."%(target.year, target.month, latest_year, latest_month))
		return target.year, target.month, 12

	# step 2-2: conduct processes for op_mode of 2
	elif op_mode == 2 : 

		# - calculate start_year, start_month, and month_range to be used for further predictions
		target = datetime.date(latest_year, latest_month, 1)
		target = target + datetime.timedelta(days=35)
		print ("Conduct prediction for 24 months from %d.%d"%(target.year, target.month))

		# - make a list of years to be considered
		year_list = [] 
		current = datetime.date(target.year, target.month, 1) 
		current = current - datetime.timedelta(days=monthrange(current.year, current.month)[1]) 
		for ridx in range(1, 24+1): 
			current = current + datetime.timedelta(days=monthrange(current.year, current.month)[1]) 
			if not current.year in year_list: 
				year_list.append(current.year) 

		# for each considered year
		for current_year in year_list:
			# - check availability of date file and generate if required
			if not os.path.isfile(folder_prediction_path + 'data/date/date_info_Y%d' % (current_year)):
				print ("The required file [./data/date/date_info_Y%d] does not exist"%(current_year))
				predict_common.gen_date_file(current_year)
				print ("The required file [./data/date/date_info_Y%d] is generated"%(current_year))

		# - remove the previously used files if any
		used_files_if_any = "rm -rf " + folder_prediction_path + "data/tmp_for_pred/*"
		os.system(used_files_if_any)

		# - copy the available files to use them temporarily
		script="cp -R"
		scr_list = ["data/date", "data/insu", "data/sub", "data/temp", "data/tmp_for_pred/"]
		for scr_box in scr_list:
			script += " " + scr_box
		os.system(script)
		## "cp -R data/date data/insu data/sub data/temp data/tmp_for_pred/"

		return target.year, target.month, 24

	

# # # # # # # # # # # # # # # # # # # # # # # #
#                M a i n                      #
# # # # # # # # # # # # # # # # # # # # # # # #

import sys
import prediction.predict_past_12months as predict_past_12months
import prediction.predict_coming_24months as predict_coming_24months
def main(area, op_mode, temp_mode, sub_mode):
	'''
	This function mainly controls predictions.
	Args:
		area: string, target area of prediction
		op_mode: int, examine prediction accuracy using the latest 1-year data (1) or conduct predictions for coming 24 months (2)
		temp_mode: int, whether to use the predicted temp (0) or the true temp (1) data
		sub_mode: int, whether to use the predicted number of subscribers (0) or the true number of subscribers (1) data
	'''

	# step 1: Check whether the required files exist AND generate the required files if possible
	start_year, start_month, month_range = check_and_prepare_data(area, op_mode, temp_mode, sub_mode)

	print("start_year: ", start_year)
	print("start_month: ", start_month)
	print("month_range: ", month_range)

	# step 2: Conduct predictions
	# - predict the latest 12 months for the purpose of analysis
	if op_mode == 1:
		predict_past_12months.conduct_prediction(area, start_year, start_month, month_range, temp_mode, sub_mode)
	# - predict coming 24 months
	elif op_mode == 2:
		predict_coming_24months.conduct_prediction(area, start_year, start_month, month_range)

# /data/insu 에서 가장 최근 파일로
# main('naju', 1, 1, 1)
#
# main("naju", 1, 1, 1)

if __name__ == "__main__":

	# step 1: Get the input parameters
	# - target area of prediction (e.g., naju, gwangju, ....)
	# area = sys.argv[1]
	area = 'naju'
	# - operational mode. 1: examine prediction accuracy using the latest 1-year data / 2: conduct predictions for coming 24 months
	# op_mode = int(sys.argv[2])
	op_mode = 2
	if op_mode != 1 and op_mode != 2:
		print ("Wrong op_mode. op_mode should be one of '1' and '2'.")
		# TODO: need a proper handling method

	# - use the predicted temp or the true numer (only available for op_mode of 1)
	# temp_mode = int(sys.argv[3])
	temp_mode = 0

	# - use the predicted subscriber number or the true numer (only available for op_mode of 1)
	# sub_mode = int(sys.argv[4])
	sub_mode = 0
	# - check input parameters and modify them if required. for op_mode of 2, '0' is only available for temp_mode and sub_mode
	if op_mode == 2 and (temp_mode + sub_mode) > 0 :
		print ("0 is only available option for temp_mode and sub_mode in case of op_mode of 2. Values are adjusted correspondingly.")
		temp_mode = 0
		sub_mode = 0

	# step 2: execute main function
	# main(area, op_mode, temp_mode, sub_mode)
	# main('naju', 2)
