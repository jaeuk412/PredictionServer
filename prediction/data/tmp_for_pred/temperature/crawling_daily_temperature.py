from bs4 import BeautifulSoup
from datetime import datetime
import requests
import sys


def extract_data(data):

	sign = 1
	sidx = 0
	eidx = 0
	for idx in range(len(data)):
		if data[idx] =="-":
			sign = -1
		try:
			ft = float(data[idx])
			if sidx == 0:
				sidx = idx
			if sidx > 0:
				eidx = idx
		except ValueError:
			continue

	try:
		value = float(data[sidx:eidx+1]) * sign 
	except ValueError:
		value = -100
	return value


def crawling_temp(area, target_year, month_list):

	f = open("%s_temp_%d"%(area, target_year), 'w')
	f.write("year month date avgTemp maxTemp minTemp\n")
	PART=["1", "11", "21"]

	if area =="gwangju" or area =="naju":
		area_code = 156
	elif area =="youngkwang":
		area_code = 252
	elif area =="haenam":
		area_code = 261
	elif area == "janheung":
		area_code = 260

	avg_temp_low = 0
	avg_temp_high = 0
	max_temp_low = 0
	max_temp_high = 0
	min_temp_low = 0
	min_temp_high = 0
	humid_low = 0
	humid_high = 0
	cloud_low = 0
	cloud_high = 0
	sun_low = 0
	sun_high = 0
	wind_low = 0
	wind_high = 0

	for month in month_list:
		for part in PART:

			if part =="1" or part == "11":
				avg_temp_low = 0
				avg_temp_high = 9
				max_temp_low = 24
				max_temp_high = 33
				min_temp_low = 48
				min_temp_high = 57
				humid_low = 96
				humid_high = 105
				cloud_low = 132
				cloud_high = 141
				sun_low = 144
				sun_high = 153
				wind_low = 180
				wind_high = 189	

			else:
				if month == 4 or month == 6 or month == 9 or month == 11:
					avg_temp_low = 0
					avg_temp_high = 9
					max_temp_low = 24
					max_temp_high = 33
					min_temp_low = 48
					min_temp_high = 57
					humid_low = 96
					humid_high = 105
					cloud_low = 132
					cloud_high = 141
					sun_low = 144
					sun_high = 153
					wind_low = 180
					wind_high = 189	

				elif month == 1 or month == 3 or month == 5 or month == 7 or month == 8 or month == 10 or month == 12:
					avg_temp_low = 0
					avg_temp_high = 10
					max_temp_low = 26
					max_temp_high = 36
					min_temp_low = 52
					min_temp_high = 62
					humid_low = 104
					humid_high = 114
					cloud_low = 143
					cloud_high = 153
					sun_low = 156
					sun_high = 166
					wind_low = 195
					wind_high = 205	

				else:
					if (target_year - 2000)%4 == 0:
						avg_temp_low = 0
						avg_temp_high = 8 
						max_temp_low = 22
						max_temp_high = 30
						min_temp_low = 44
						min_temp_high = 52
						humid_low = 88 
						humid_high = 96 
						cloud_low = 121
						cloud_high = 129
						sun_low = 132
						sun_high = 140
						wind_low = 165
						wind_high = 173	
					else:
						avg_temp_low = 0
						avg_temp_high = 7 
						max_temp_low = 20
						max_temp_high = 27
						min_temp_low = 40
						min_temp_high = 47
						humid_low = 80 
						humid_high = 87 
						cloud_low = 110
						cloud_high = 117
						sun_low = 120
						sun_high = 127
						wind_low = 150
						wind_high = 157	
		
			url = "http://www.weather.go.kr/weather/climate/past_tendays.jsp?stn=%d&yy=%d&mm=%d&obs=%s&x=26&y=10" % (area_code, target_year, month, part)
			web_page = requests.get(url)
			soup = BeautifulSoup(web_page.text, "html.parser")

			index = 0
			avg_temp=[]
			max_temp=[]
			min_temp=[]
		
			table_data = soup.find_all('td')
			for soup_data in table_data:
				data = str(soup_data)	
				if len(data) > 110:
					if index >= avg_temp_low and index <= avg_temp_high:
						avg_temp.append(extract_data(data))
					if index >= max_temp_low and index <= max_temp_high:
						max_temp.append(extract_data(data))
					if index >= min_temp_low and index <= min_temp_high:
						min_temp.append(extract_data(data))
					#print (index, avg_temp_low, avg_temp_high, data)
					index += 1
			
			for i in range(len(avg_temp)):
				file_input = "%s %02d %02d %.2f %.2f %.2f\n" %(target_year, int(month), int(part)+i, avg_temp[i], max_temp[i], min_temp[i])
				f.write(file_input)

	f.close()


# area = sys.argv[1]
# target_year = int(sys.argv[2])
# today = datetime.today()
# if target_year < today.year:
# 	month_list = range(1,13,1)
# elif target_year == today.year:
# 	month_list = range(1, today.month)

# crawling_temp(area, target_year, month_list)

# crawling_temp('naju', 2022, [1,2,3,4,5,6,7,8,9,10,11,12])
