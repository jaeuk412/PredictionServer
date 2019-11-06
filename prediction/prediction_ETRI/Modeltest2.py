import re

file_name_get_model =  "<numeric>lwm2m/dex-iot-0001/22000/0/5700"
pat = re.compile("lwm2m[^:]+/")
patfilter = pat.findall(file_name_get_model)

print(patfilter)