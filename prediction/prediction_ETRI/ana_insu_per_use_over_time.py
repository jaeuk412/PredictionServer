from calendar import monthrange
import pandas as pd
import numpy as np
from API.api_helper.user_directory import folder_path

def ana_insu_per_use_over_time(area, start_year, end_year):

	if start_year > end_year:
		print ("start_year should be less than end_year")
		return

	all_category = ['house', 'houseCooking', 'houseJHeating', 'houseCHeating',  'salesOne', 'salesTwo', 'bizHeating', 'bizCooling', 'industry', 'heatFacility', 'heatCombined', 'CNG']

	for cat in all_category :
		print (cat)
		x_feat = ['sub_%s'%(cat)]
		y_feat = ['insu_%s'%(cat)] 

		for tyear in range(start_year, end_year+1): 
			try: 
				insu_data = pd.read_csv('data/insu/%s_insu_%d'%(area, tyear), delim_whitespace=True) 
			except Exception as e:
				print ("The required file [./data/insu/%s_insu_%d] does not exist. This file should be prepared by HyGAS"%(area, tyear)) 
				return 

			try: 
				sub_data = pd.read_csv('data/sub/%s_sub_%d'%(area, tyear), delim_whitespace=True) 
			except FileNotFoundError:
				print ("The required file [./data/sub/%s_sub_%d] does not exist. This file should be prepared by HyGAS"%(area, tyear)) 
				return 

			print ("%d : "%(tyear), end='')

			for tmon in range(1, 13):

				## [sub] 해당 월(tmon)의 1일 - 말일 까지 모든 데이터 가져옴.
				sub_same_month = sub_data[sub_data['month']==tmon]

				## 매월(tmon) 월의 날 개수(mon_days) ex-> 1월은 mon_days=31
				mon_days = monthrange(tyear, tmon)[1]

				## [sub] 매월 의 1일.
				first_day = sub_same_month[sub_same_month['date']==1]

				## [sub]의 category(house, houseCHeating ...)의 각 1일 에 해당하는 값
				sub_num = first_day[x_feat].values[0]

				insu_sum = 0
				## [insu] 해당 월(tmon)의 1일 - 말일 까지 모든 데이터 가져옴.
				insu_same_month = insu_data[insu_data['month']==tmon] 
				for tday in range(1, mon_days+1):

					# [insu]의 각 일에 따른 데이터 값.
					target_day = insu_same_month[insu_same_month['date']==tday]

					# 각 category의 1월1일 부터 12월 31까지 나온 각 값의 합.
					insu_sum += target_day[y_feat].values[0]

				print ("%d %.2f "%(sub_num, insu_sum), end='')
				if sub_num > 0:
					print ("%.2f , "%(insu_sum/sub_num), end='')
				else:
					print ("n/a , ", end='')
				
			print ("")
# insu: 인수량, sub:세대수
# 해당년도, [sub] house의 1월 세대수, [insu]house 1월 사용량, 1세대 당 사용 인수량 평균 / housecooking /....
def main(area, start_year, end_year):
	ana_insu_per_use_over_time(area, start_year, end_year)

main('naju',2015,2015)
# import sys
# def main():
# 	area = sys.argv[1]
# 	start_year = int(sys.argv[2])
# 	end_year = int(sys.argv[3])
#
# 	ana_insu_per_use_over_time(area, start_year, end_year)
#
#
# if __name__ == "__main__":
#         main()
