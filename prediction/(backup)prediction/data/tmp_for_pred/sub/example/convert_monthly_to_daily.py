import pandas as pd
import numpy as np
import sys
from calendar import monthrange

data = pd.read_csv(sys.argv[1], delim_whitespace=True)

print ("year month date sub_house sub_houseCooking sub_houseJHeating sub_houseCHeating sub_salesOne sub_salesTwo sub_bizHeating sub_bizCooling sub_industry sub_heatFacility sub_heatCombined sub_CNG")

data = np.array(data)
for idx in range(len(data)):
	current_year = data[idx][0]
	current_month = data[idx][1]
	
	current_house = data[idx][2]
	current_houseCooking = data[idx][3]
	current_houseJHeating = data[idx][4]
	current_houseCHeating = data[idx][5]

	current_salesOne = data[idx][6]
	current_salesTwo = data[idx][7]

	current_bizHeating = data[idx][8]
	current_bizCooling = data[idx][9]

	current_ind = data[idx][10]

	current_heatOne = data[idx][11]
	current_heatTwo = data[idx][12]

	current_cng = data[idx][13]

	num_days = monthrange(int(current_year), int(current_month))[1]

	for tidx in range(num_days):
		print (current_year, current_month, tidx+1, current_house, current_houseCooking, current_houseJHeating, current_houseCHeating,  current_salesOne, current_salesTwo, current_bizHeating, current_bizCooling, current_ind, current_heatOne, current_heatTwo, current_cng)
