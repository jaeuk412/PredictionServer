import numpy as np
import sys

from bs4 import BeautifulSoup
import pandas as pd
import requests
def get_date_info(mode, year, month):

	if mode == 0:
        	url='http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getHoliDeInfo?solYear=%d&solMonth=%02d&'%(year, month)
        	key = 'ServiceKey=z6zyiFzd2GyGZ3JeqRPFQ4%2FJCLK1dwN2nBAEFtL1y5R2HBPmLkZYEUVwLNYyDZJStRi8zT%2B9nnxMbwjUzchSQg%3D%3D'
        	url=url+key
	elif mode == 1:
        	url='http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getRestDeInfo?solYear=%d&solMonth=%02d&'%(year, month)
        	key = 'ServiceKey=z6zyiFzd2GyGZ3JeqRPFQ4%2FJCLK1dwN2nBAEFtL1y5R2HBPmLkZYEUVwLNYyDZJStRi8zT%2B9nnxMbwjUzchSQg%3D%3D'
        	url=url+key
	elif mode == 2:
        	url='http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/get24DivisionsInfo?solYear=%d&solMonth=%02d&'%(year, month)
        	key = 'ServiceKey=z6zyiFzd2GyGZ3JeqRPFQ4%2FJCLK1dwN2nBAEFtL1y5R2HBPmLkZYEUVwLNYyDZJStRi8zT%2B9nnxMbwjUzchSQg%3D%3D'
        	url=url+key
	else:
        	url='http://apis.data.go.kr/B090041/openapi/service/SpcdeInfoService/getSundryDayInfo?solYear=%d&solMonth=%02d&'%(year, month)
        	key = 'ServiceKey=z6zyiFzd2GyGZ3JeqRPFQ4%2FJCLK1dwN2nBAEFtL1y5R2HBPmLkZYEUVwLNYyDZJStRi8zT%2B9nnxMbwjUzchSQg%3D%3D'
        	url=url+key

	req = requests.get(url)
	html = req.text
	soup = BeautifulSoup(html, 'html.parser')

	holiday_list = []
	for element in soup.findAll('item'): 
		date = element.locdate.string 
		#print ("%s %s %s %s"%(date[0:4], date[4:6], date[6:8], element.datename.string)) 
		holiday_list.append("%s%s%s"%(date[0:4], date[4:6], date[6:8]))

	return holiday_list


import datetime
def get_day_info(year, month, date):

	day_code = datetime.date(year, month, date).weekday()

	return day_code


def check_holiday(holiday_list, year, month, date):
	target_day = "%d%02d%02d"%(year, month, date)
	holiday_list = np.array(holiday_list)
	is_holiday = 0
	if len(holiday_list) > 0:
		for tlist in holiday_list:
			if target_day in tlist:
				is_holiday = 1

	return is_holiday

from calendar import monthrange
def gen_date_info(target_year):

	f = open("date_info_Y%d"%(target_year), 'w')
	f.write("year month date day holiday\n")
	for tmon in range(1,13):

		holiday_list = get_date_info(1, target_year, tmon)
		mon_days = monthrange(target_year, tmon)[1] 
		for tday in range(1, mon_days+1): 
			day_code = get_day_info(target_year, tmon, tday)
			holiday_code = check_holiday(holiday_list, target_year, tmon, tday)
			file_input = "%d %d %d %d %d\n"%(target_year, tmon, tday, day_code, holiday_code)
			f.write(file_input)

	f.close()

# gen_date_info(int(sys.argv[1]))

# gen_date_info(2021)
