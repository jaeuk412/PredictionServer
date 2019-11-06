import pandas as pd
import numpy as np


raw_data = pd.read_csv('merged_naju_2014_2018', delim_whitespace=True)

tmp_year = raw_data[raw_data['year']== 2014]

new_tmp_year = tmp_year.drop(columns=['avgTemp', 'maxTemp', 'minTemp'])

print (new_tmp_year)
