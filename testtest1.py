import os
from API.api_helper.user_directory import root_path, folder_detectkey_path
import time



w_break = 0
while 1:
    if w_break == 1:
        break

    ## temp 붙은 파일 삭제 (추후 자동 업데이트로)
    files = os.listdir(folder_detectkey_path)
    print(files)
    for i in files:
        if 'temp' in i:
            print('in_temp')
            w_break=1
        else:
            print('pass')
            pass
