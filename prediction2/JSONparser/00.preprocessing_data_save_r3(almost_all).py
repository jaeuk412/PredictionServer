# -*- coding: utf-8 -*-
# !/usr/bin/env python
# coding: utf-8
'''
1. 입력값 json 형태로 변수화.

입력값(input_value): {
                    'bms':
                        {
                         '1803': ['VCell', 'VCellMax', 'VCellMin'],
                         '802': ['A', 'AChaMax', 'ADisChaMax', 'SoC', 'SoH', 'V']
                        },
                    'pcs--ess':
                        {
                        '113': ['DCA', 'DCV', 'DCW', 'VAr', 'W']
                        }
                    }
2. 저장소(이어하기) 옵션: reset=True(저장소 내용 지우고 초기화), reset=False(기존 csv 내용 이어서 진행((저장위치:tar_frame_save_list/[해당 folder_name])))
3. 변수(input_value)를 바꾼 후 실행 시, 이미 진행된(기존) 폴더로 이어하기 하면 변수가 불일치하여 저장안됨. 기존 저장소 폴더 및 파일을 별도 저장 후 실행바람.

- 개발 진행된 라이브러리.
pandas = 0.22.0
matplotlib = 3.0.3
sklearn = 0.0

-기타 사항.
< padnas: 0.23 버전 이후 부터 concet 경고(w) 발생(실행에 문제는 없는 듯) -> sort=True or pandas 0.23 이전 버전 사용바람. >
'''

# In[18]:


import pandas as pd
import csv
import json
import os
import matplotlib.pyplot as plt
import matplotlib as rc
from operator import eq

from sklearn.preprocessing import MinMaxScaler

# In[19]:


#######################################################
######### 변수 및 경로 선언.
#######################################################

# folder_path = 현재 디렉토리 + '/30'(folder_name)
# 저장소(이어하기) 폴더도 해당 폴더명([folder_name])을 따라 폴더 저장. ~/tar_frame_save_list/[folder_name]/저장.csv
folder_name = '/32'
folder_path = os.getcwd() + '/jsondatafile' +folder_name

# reset = False -> 기존 했던 부분부터 이어서 start.
# reset = True  -> 이어하기 저장소 파일 목록(.txt, .csv) 초기화.
reset = True

# json 형태. (target_device=[], target_value={}, target_id={})
input_value = {
    'bms': {'802': ['A', 'AChaMax', 'ADisChaMax', 'SoC', 'SoH', 'V'],
            '1803': ['VCell', 'VCellMax', 'VCellMin']},
    'pcs--ess': {'113': ['DCA', 'DCV', 'DCW', 'VAr', 'W']}}

# target_device = ['bms','pcs--ess']
# target_value = {'bms':['802','1803'],'pcs--ess':['113'] }
# target_id = {'802':['A','AChaMax','ADisChaMax','SoC','SoH','V'], '1803':['VCell','VCellMax','VCellMin'], '113':['DCA','DCV','DCW','VAr','W']}


font_size = 20


#######################################################

def set_value(input_value):
    target_device = []
    target_id = {}
    target_value = {}

    for t_device in sorted(input_value.keys()):
        # target_device
        target_device.append(t_device)
        # target_id
        t_value = input_value.get(t_device)
        target_id.update(t_value)
        target_id_key_value = {}
        target_id_key = []

        for t_id in sorted(t_value.keys()):
            target_id_key.append(t_id)
            target_id_key_value[t_device] = target_id_key
            # target_value
            target_value.update(target_id_key_value)

    return target_device, target_value, target_id


# tar_frame_already_done_list
tar_frame_save_folder = os.getcwd() + '/tar_frame_save_list' + folder_name  ## 이어하기 옵션(reset) 저장 폴더.
tar_frame_done_txt = '/already_done_list.txt'  ## 진행된 .csv 파일 리스트
tar_frame_done_csv = '/tar_frame.csv'  ## 진행된 .csv의 최종 결과를 저장.
tar_frame_variable_txt = '/variable.txt'  ## input 값 정보를 저장.

target_device, target_value, target_id = set_value(input_value)

print("folder_path: ", folder_path)
print("target_device: ", target_device)
print("target_value: ", target_value)
print("target_id: ", target_id)

plot_title = '_'.join(target_device) + '_' + '_'.join([key for key in target_id])


# In[20]:

# 폴더안의 파일을 리스트화.
def file_read():
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(folder_path):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]

    listOfFiles.sort()

    print("file_read: ", listOfFiles)
    print(" - - -")
    return listOfFiles


def make_list():  # data frame column 구성에 사용

    tot_list = []
    for td in target_device:
        tv = target_value[td]
        tv_list = []

        # print("tv: ",tv)

        for i in tv:
            ti = target_id[i]
            # target=json_data[td].loc[i]

            ti_list = []
            for j in range(len(ti)):
                # ti_list.append(ti[j])
                ti_list.append(td + '_' + str(i) + '_' + ti[j])

            tv_list.extend(ti_list)
        tot_list.extend(tv_list)
    # print("tot_list: ",tot_list) # total_list

    return tot_list


# # In[22]:


def feature_ext(json_data):
    tar_list = []

    for td in target_device:
        tv = target_value[td]
        tv_list = []
        # print("tv: ",tv)

        for i in tv:
            ti = target_id[i]
            # print(td,i)
            target = json_data[td].loc[int(i)]
            # print(target)

            ti_list = []
            for j in range(len(ti)):
                ti_list.append(target[ti[j]])

            tv_list.extend(ti_list)
        tar_list.extend(tv_list)
    # print("tar_list: ",tar_list) # total_list

    return tar_list


# In[23]:

##------------------------------------------------------------------------------------------------
## pandas 0.23 이후 버전 부터 sort=True warnming, 문제는 없는듯.
def list2pd(tar_list, df):
    pdf = pd.DataFrame(tar_list, columns=make_list())  # column head 수정
    pd_con = pd.concat([pdf, df['timestamp']], axis=1)

    # try:
    #     pd_con.to_csv(tar_frame_save_folder+'/tar_frame.csv', mode='a', index=False)
    # except Exception as e:
    #     return print(e)

    return pd_con


# In[24]:


def visualization1(tar_frame):
    tar_frame_time = tar_frame.copy()

    #    tar_frame_time[target_value_02].plot(kind='line', figsize=(20,6), linewidth=3, fontsize=font_size, x = "Time")
    tar_frame_time.plot(kind='line', figsize=(20, 6), linewidth=3, fontsize=font_size, x="timestamp")
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5), fontsize=font_size)
    plt.title(plot_title, fontsize=font_size)
    plt.xlabel('Index', fontsize=font_size)
    plt.ylabel('Demand', fontsize=font_size)

    plt.locator_params(axis='x', nbins=4)

    plt.show()


# In[25]:


def visualization2(tar_frame):
    min_max_scaler = MinMaxScaler()

    drop_frame = tar_frame.drop(['timestamp'], axis=1)
    fit_data = min_max_scaler.fit(drop_frame)

    tar_frame_norm = min_max_scaler.transform(drop_frame)
    tar_frame_norm = pd.DataFrame(tar_frame_norm, columns=drop_frame.columns, index=list(drop_frame.index.values))

    tar_frame_time = tar_frame_norm.copy()
    tar_frame_time["Time"] = tar_frame['timestamp']

    #    tar_frame_time[target_value_02].plot(kind='line', figsize=(20,6), linewidth=3, fontsize=font_size, x = "Time")
    tar_frame_time.plot(kind='line', figsize=(20, 6), linewidth=3, fontsize=font_size, x="Time")
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5), fontsize=font_size)
    plt.title(plot_title, fontsize=font_size)
    plt.xlabel('Index', fontsize=font_size)
    plt.ylabel('Demand', fontsize=font_size)

    plt.locator_params(axis='x', nbins=4)

    plt.show()


# In[26]:


def feature_save(tar_frame):
    save_fname = plot_title + '.pickle'

    if os.path.exists(save_fname):
        print(
            'Warning!! The same file name exists. If you are sure you want to create a new file, delete the file first. ')
        return
    else:
        print('A new file will be created. ')
        # get_ipython().run_line_magic('time', 'tar_frame.to_pickle(save_fname)')

    return


## 저장소 txt 및 csv 제거.
def file_remove(reset):
    ## 만약 reset(True)을 받으면 기존 데이터 지우고 처음부터. tar_frame.csv도 삭제.
    if reset == True:
        if os.path.isfile(tar_frame_save_folder + tar_frame_done_csv):
            os.remove(tar_frame_save_folder + tar_frame_done_csv)

        if os.path.isfile(tar_frame_save_folder + tar_frame_variable_txt):
            os.remove(tar_frame_save_folder + tar_frame_variable_txt)

        if os.path.isfile(tar_frame_save_folder + tar_frame_done_txt):
            os.remove(tar_frame_save_folder + tar_frame_done_txt)


## txt 파일 저장.
def file_save(file_name):
    # print("file_name: ",file_name)
    file_path = tar_frame_save_folder + tar_frame_done_txt

    # folder_detect()
    file_detect()

    ## 저장된 tar_frame(csv경로)를 리스트로 만듬.
    with open(file_path, 'r') as f:
        file_list = f.read().splitlines()
    ## 리스트에 csv경로 주소 저장.
    if str(file_name) in file_list:
        pass
    else:
        with open(file_path, 'a') as f:
            f.write(file_name + '\n')


## 저장 경로 directory 및 파일 유무 확인.
def file_detect():
    file_path = tar_frame_save_folder + tar_frame_done_txt

    ## 'tar_frame' 최상위 폴더가 없다면 만듬.
    if not os.path.isdir(tar_frame_save_folder):
        os.makedirs(tar_frame_save_folder)
        pass

    ## 'already_dnoe_list.txt' or 'tar_frame.csv'가 없으면 초기화해서 새로 시작.
    if not os.path.isfile(file_path) or not os.path.isfile(tar_frame_save_folder + tar_frame_done_csv):
        print("####################################################################################################")
        print("#########             There is no record file           * create new record file *         #########")
        print("####################################################################################################")
        file_remove(True)


## 기존에 진행된 csv 리스트 체크.
def file_check(file_name):
    file_detect()

    ## frame_done.txt가 없으면 새로 만듬.
    if not os.path.isfile(tar_frame_save_folder + tar_frame_done_txt):
        with open(tar_frame_save_folder + tar_frame_done_txt, 'w'):
            pass

    with open(tar_frame_save_folder + tar_frame_done_txt, 'r') as f:
        filelist = f.read().splitlines()

    if str(file_name) in filelist:
        print("----already done----")
        print(file_name)
        return True
    else:
        print('----new_file----')
        print(file_name)
        return False


## tar_frame.csv 저장.
def tar_save(tar_frame, starget_id):
    try:
        pdf = pd.DataFrame(tar_frame)  # column head 수정
        # pdf.to_csv(tar_frame_save_folder+'/tar_frame.csv',header=True, index=True, )
        if not os.path.isfile(tar_frame_save_folder + tar_frame_done_csv):
            ## tar_frame_done.csv, variable.txt 최초 1번 생성.
            pdf.to_csv(tar_frame_save_folder + tar_frame_done_csv, header=True, index=False)

            ## variable 저장.
            variable_save(starget_id)
        else:
            if not os.path.isfile(tar_frame_save_folder + tar_frame_variable_txt):
                variable_save(starget_id)
            # pdf.to_csv(tar_frame_save_folder + tar_frane_csv, header=True, index=True)
            pdf.to_csv(tar_frame_save_folder + tar_frame_done_csv, header=False, index=False, mode='a')

        # with open(tar_frame_save_folder+'/tar_frame.csv', 'a') as f:
        #     f.write(tar_frame)
    except Exception as e:
        return print(e)


## tar_frame.csv 내용 읽기.
def tar_frame_read():
    if not os.path.isfile(tar_frame_save_folder + tar_frame_done_csv):
        return print("===========There is no tar_frame.csv, please restart reset=True==========")

    data = pd.read_csv(tar_frame_save_folder + tar_frame_done_csv)

    return data


## 사용 변수 tar_frame.csv 만들 때 처음 1번 저장.
def variable_save(starget_id):
    file_path = tar_frame_save_folder + tar_frame_variable_txt
    with open(file_path, 'w') as f:
        f.write(str(starget_id) + '\n')

    return


## 사용 변수 체크.
def variable_check(ctarget_id):
    # input_value_now = sorted(input_value_now)
    file_path = tar_frame_save_folder + tar_frame_variable_txt

    if not os.path.isfile(file_path):
        return True
    else:
        with open(file_path, 'r') as f:
            saved_file = f.read()

        check_variable = ctarget_id
        saved_file = eval(saved_file)

        if check_variable.items() == saved_file.items():
            return True
        else:
            print("\n** Not the same Variable  Please check your variable. **\n")
            print("** Cannot Save all information in the tar_frame_save.csv/txt **\n")
            print("NewInput_value: ", check_variable)
            print("Original_value: ", saved_file, "\n")

            return False


# In[29]:


tar_frame = pd.DataFrame()


## 시행 함수.
def circle(file_name, tar_frame):
    tar_list = []

    data = pd.read_csv(file_name, names=['bms', 'timestamp'])
    df = pd.DataFrame(data)

    tar_list = []
    for json_raw in range(len(df.index)):
        try:
            json_data = pd.read_json(df['bms'].iloc[json_raw])  # json_data : pandas format
            # print("json_data: ",json_data)
            tar_list.append(feature_ext(json_data))
            print("tttt: ",tar_list)
        except ValueError:
            pass

    print("tar_list: ", tar_list)
    # print("tar_list_len: ", len(tar_list))

    try:
        tar_box_to_save = (list2pd(tar_list, df)).reset_index(drop=True)
        if variable_check(target_id) == True:
            tar_save(tar_box_to_save, target_id)
            tar_frame = tar_frame.append(tar_box_to_save)
            file_save(file_name)
        else:
            return False

    except Exception as e:
        return print(e)

    return tar_frame


def main():
    global tar_frame

    file_list = file_read()

    ## reset 체크, True 일 때 저장소 초기화.
    if reset == True:
        print("####################################################################################################")
        print("#########    reset = T ( reset=T - remove save data, reset=F - continue save data )         ########")
        print("####################################################################################################")

    file_remove(reset)

    j = False

    for file_name in file_list:

        ## 진행된 csv 리스트 check.
        if file_check(file_name) == True:
            # print('--------------------1--------------------')
            ## tar_frame.csv에 내용 있으면 사용(최초 한번(j=False)).
            if os.path.isfile(tar_frame_save_folder + tar_frame_done_csv):
                if j == False:
                    tar_frame = tar_frame_read()
                    j = True
            ## csv 저장 내용 없을시 circle() 시행.
            else:
                tar_frame = circle(file_name, tar_frame)

        ## 파일 리스트 없다면 circle() 시행.
        else:
            tar_frame = circle(file_name, tar_frame)

    feature_save(tar_frame)

    visualization1(tar_frame)
    visualization2(tar_frame)


# In[30]:


if __name__ == "__main__":
    main()

    print(tar_frame)

# In[ ]:


# In[31]:


# tar_frame.head()


# In[ ]:




