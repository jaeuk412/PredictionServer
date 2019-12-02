from calendar import monthrange
import pandas as pd
import numpy as np

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
				insu_sub_data = pd.read_csv('data/insu_sub/%s_insu_sub_%d'%(area, tyear), delim_whitespace=True) 
			except FileNotFoundError: 
				print ("The required file [./data/insu_sub/%s_insu_sub_%d] does not exist. This file should be prepared by HyGAS"%(area, tyear)) 
				return 

			print ("%d : "%(tyear), end='')

			for tmon in range(1, 13): 

				prev_same_month = insu_sub_data[insu_sub_data['month']==tmon] 
	
				mon_days = monthrange(tyear, tmon)[1] 

				first_day = prev_same_month[prev_same_month['date']==1] 
				sub_num = first_day[x_feat].values[0]

				insu_sum = 0
				for tday in range(1, mon_days+1): 
					target_day = prev_same_month[prev_same_month['date']==tday] 
					insu_sum += target_day[y_feat].values[0]

				print ("%d %.2f "%(sub_num, insu_sum), end='')
				if sub_num > 0:
					print ("%.2f , "%(insu_sum/sub_num), end='')
				else:
					print ("n/a , ", end='')
				
			print ("")


import sys
def main():
	area = sys.argv[1]
	start_year = int(sys.argv[2])
	end_year = int(sys.argv[3])

	ana_insu_per_use_over_time(area, start_year, end_year)


if __name__ == "__main__":
        main()
