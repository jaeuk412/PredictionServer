import pandas as pd
import numpy as np
import sys
from calendar import monthrange
from scipy.optimize import curve_fit



def ana_insu_per_use_over_time(file_name):
	all_category = ['house', 'houseCooking', 'houseJHeating', 'houseCHeating',  'salesOne', 'salesTwo', 'bizHeating', 'bizCooling', 'industry', 'heatFacility', 'heatCombined', 'CNG']

	raw_data = pd.read_csv(file_name, delim_whitespace=True)

	for cat in all_category :
		print (cat)
		x_feat = ['sub_%s'%(cat)]
		y_feat = ['insu_%s'%(cat)]

		for tyear in [2014, 2015, 2016, 2017, 2018]: 
			print ("%d : "%(tyear), end='')
			prev_same_year = raw_data[raw_data['year']==tyear] 

			for tmon in range(1, 13): 

				prev_same_month = prev_same_year[prev_same_year['month']==tmon] 
	
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



ana_insu_per_use_over_time(sys.argv[1])
