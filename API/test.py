from API.api_helper.user_directory import root_path

path = root_path + '/detectkey/'+"tetst.txt"

with open(path,'w') as f:
    f.write("123")