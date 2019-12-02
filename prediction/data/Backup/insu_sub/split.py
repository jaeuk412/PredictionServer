import pandas as pd
import numpy as np


raw_data = pd.read_csv('merged_naju_2014_2018', delim_whitespace=True)

tmp_year = raw_data[raw_data['year']== 2014]

new_tmp_year = tmp_year.drop(columns=['avgTemp', 'maxTemp', 'minTemp'])

print("year month date insu_house insu_houseCooking insu_houseJHeating insu_houseCHeating insu_salesOne insu_salesTwo insu_bizHeating insu_bizCooling insu_industry insu_heatFacility insu_heatCombined insu_CNG sub_houseTotal sub_house sub_houseCooking sub_houseJHeating sub_houseCHeating sub_salesTotal sub_salesOne sub_salesTwo sub_bizTotal sub_bizHeating sub_bizCooling sub_industry sub_heatFacility sub_heatCombined sub_CNG")
for index, row in new_tmp_year.iterrows():
    print("%d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d %d"%(row['year'], row['month'], row['date'], row['insu_house'], row['insu_houseCooking'], row['insu_houseJHeating'], row['insu_houseCHeating'], row['insu_salesOne'], row['insu_salesTwo'], row['insu_bizHeating'], row['insu_bizCooling'], row['insu_industry'], row['insu_heatFacility'], row['insu_heatCombined'], row['insu_CNG'], row['sub_houseTotal'], row['sub_house'], row['sub_houseCooking'], row['sub_houseJHeating'], row['sub_houseCHeating'], row['sub_salesTotal'], row['sub_salesOne'], row['sub_salesTwo'], row['sub_bizTotal'], row['sub_bizHeating'], row['sub_bizCooling'], row['sub_industry'], row['sub_heatFacility'], row['sub_heatCombined'], row['sub_CNG']))
