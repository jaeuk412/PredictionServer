# -*- coding: utf-8 -*-
# json 입력 값 받아서, 불필요 변수와, Null값 제거.

'''
1. 입력값 json 형태로 변수화.
2. 저장소(이어하기) 옵션: reset=True(저장소 내용 지우고 초기화), reset=False(기존 csv 내용 이어서 진행((저장위치:tar_frame_save_list/[해당 folder_name])))
3. input 값에 따라 폴더명으로 저장.

# 추가.
4. 데이터는 "jsondatafile/" 폴더에 꼭 넣어야함.
5. parsing된 파일 저장 위치: "tar_frame_save_list/폴더명(변수이름+시작날짜폴더)/tar_frame.csv"
6. 저장된 파일의 값을 기준으로, key, value 값 parsing.

- 개발 진행된 라이브러리.
pandas = 0.22.0
matplotlib = 3.0.3
sklearn = 0.0

-기타 사항.
< padnas: 0.23 버전 이후 부터 concet 경고(w) 발생(실행에 문제는 없는 듯) -> sort=True or pandas 0.23 이전 버전 사용바람. >
'''
import pandas as pd
import csv
import json
import os
import matplotlib.pyplot as plt
import matplotlib as rc
from operator import eq
from sklearn.preprocessing import MinMaxScaler

#######################################################
######### 변수 및 경로 선언.
#######################################################


# backup 폴더 선택.
folder_name = '/' # /:None, /30 폴더명
if not folder_name:
    folder_name = '/'
folder_path = os.getcwd() + '/jsondatafile' + folder_name


# 'bms', 'meter--ess', 'meter--grid', 'meter--load', 'meter--pv', 'pcs--ess', 'pcs--pv', 'pms', 'racks'
input_value = ['bms', 'meter--ess', 'meter--grid', 'meter--load', 'meter--pv', 'pcs--ess', 'pcs--pv', 'pms', 'racks']

# bms_1805_NRackCellBal
def folder_get_name(value, folder_name):
    value_name = str()
    for i in value:
            value_name += '%s,'%(i)
    folder_name = folder_name.replace("/","")
    if not folder_name:
        folder_name = 'root'
    value_name += folder_name
    return value_name

# for save
reset = False # True=처음부터, False=이어하기
# reset = True # True=처음부터, False=이어하기
tar_frame_save_folder = os.getcwd() + '/tar_frame_save_list/' + folder_get_name(input_value,folder_name)  ## 이어하기 옵션(reset) 저장 폴더.
tar_frame_done_txt = '/already_done_list.txt'  ## 중간 결과 진행 리스트
tar_frame_done_csv = '/tar_frame.csv'  ## 중간 결과 .csv로 저장.
tar_frame_variable_txt = '/variable.txt'  ## variable(변수) 정보를 저장.
font_size = 20


def depth(json_v):
    json_v = str(json_v)
    count_in = 0
    depth = 0
    for i in range(len(json_v)):
        if json_v[i] == '{':
            count_in += 1
        if json_v[i] == '}':
            count_in -= 1
        if depth < count_in:
            depth = count_in
    return depth

# 폴더안의 파일을 리스트화.
def file_read():
    listOfFiles = list()
    for (dirpath, dirnames, filenames) in os.walk(folder_path):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]

    listOfFiles.sort()

    print("file_read: ", listOfFiles)
    print(" - - -")
    return listOfFiles

def search_values_name(key2_value, key):
    depth1 = []
    result_list =[]
    key_name_list = []

    if type(key2_value) is dict:
        for key3 in sorted(key2_value.keys()):
            key_name = str()
            key3_value = key2_value.get(key3)
            key_name += str(key) + '_' + str(key3)
            aa, result, depthv = search_values_name(key3_value, key_name)
            if result:
                result_list = result_list + result
            else:
                result_list = result_list + [0]
            if depthv:
                depth1.append(depthv)
            key_name_list = key_name_list + aa
    else:
        if key2_value:
            result_list = result_list + [key2_value]
            key_name_list = key_name_list + [key]
        else:
            result_list = result_list + [0]
            key_name_list = key_name_list + [key]

    return key_name_list, result_list, depth1

def get_json_values(input_value, get_value):
    try:

        result_depth1 = []
        keyname_list = []
        result_list = []
        for key1 in sorted(input_value.keys()):
            key_edit = str(get_value) + '_' + key1
            key1_value = input_value.get(key1)
            keyname, result_value, depth1 = search_values_name(key1_value, key_edit)
            if depth1:
                result_depth1.append(depth1)
            if keyname:
                keyname_list = keyname_list + keyname
            if result_value:
                result_list = result_list + result_value
        return keyname_list, result_list
    except:
        pass


# In[23]:

##------------------------------------------------------------------------------------------------
## pandas 0.23 이후 버전 부터 sort=True warnming, 문제는 없는듯.
def list2pd(tar_list, df, tar_name):
    pdf = pd.DataFrame(tar_list, columns=tar_name)  # column head 수정
    pd_con = pd.concat([pdf, df['timestamp']], axis=1)
    return pd_con


# In[24]:

# plot_title = '_'.join(target_device) + '_' + '_'.join([key for key in target_id])
plot_title = 'test' + '_' + 'test'
## bms_pcs--ess_802_1803_113

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
            pdf.to_csv(tar_frame_save_folder + tar_frame_done_csv, header=True, index=True)

            ## variable 저장.
            variable_save(starget_id)
        else:
            if not os.path.isfile(tar_frame_save_folder + tar_frame_variable_txt):
                variable_save(starget_id)
            pdf.to_csv(tar_frame_save_folder + tar_frame_done_csv, header=False, index=True, mode='a')

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
def variable_check(tot_list):
    # input_value_now = sorted(input_value_now)
    file_path = tar_frame_save_folder + tar_frame_variable_txt

    if not os.path.isfile(file_path):
        return True
    else:
        with open(file_path, 'r') as f:
            saved_file = f.read()

        check_variable = tot_list
        # print(type(check_variable))
        saved_file = eval(saved_file)
        # print(type(saved_file))

        # 중복되는 리스트 개수 체크.
        check_count_list = list(set(check_variable).intersection(saved_file))


        if len(check_count_list) == len(saved_file):
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

    data = pd.read_csv(file_name, names=['bms', 'timestamp'])
    df = pd.DataFrame(data)

    tar_list = []
    sum_tar_value = []
    sum_tar_name = []
    each_input_count = 0
    for each_input_value in input_value:
        for index, row in df.iterrows():
            try:
                date = row['bms']
                jso = json.loads(date)
                jso_v = jso.get(each_input_value)

                if jso_v:
                    tar_name, get_tar_list = get_json_values(jso_v, each_input_value)
                    if each_input_count == 0:
                        sum_tar_value.append(get_tar_list)
                    else:
                        sum_tar_value[index] = sum_tar_value[index] + get_tar_list
                    if index == 0:
                        sum_tar_name.extend(tar_name)
                else:
                    # 'meter--load' 처럼 값이 아에 없을 경우 key 이름만.
                    if index == 0:
                        sum_tar_name.extend([each_input_value])
                    get_tar_list = [0]
                    if each_input_count == 0:
                        sum_tar_value.append(get_tar_list)
                    else:
                        sum_tar_value[index] = sum_tar_value[index] + get_tar_list

            except ValueError:
                pass

        each_input_count += 1

    for value in sum_tar_value:
        tar_list.append(value)

    try:
        tar_box_to_save = (list2pd(tar_list, df, sum_tar_name)).reset_index(drop=True)
        # tar_box_to_save = (list2pd(get_tot_list, tar_list, df))
        if variable_check(input_value) == True:
            tar_save(tar_box_to_save, input_value)
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
                # print('--------------------2--------------------')
                tar_frame = circle(file_name, tar_frame)

        ## 파일 리스트 없다면 circle() 시행.
        else:
            # print('--------------------3--------------------')
            tar_frame = circle(file_name, tar_frame)

    feature_save(tar_frame)
    print(tar_frame)

    visualization1(tar_frame)
    visualization2(tar_frame)


# In[30]:


if __name__ == "__main__":
    main()

    print(tar_frame)



# tar_frame.head()


# In[ ]:




