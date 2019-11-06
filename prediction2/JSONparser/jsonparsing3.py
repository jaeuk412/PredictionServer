# -*- coding: utf-8 -*-
# json 입력 값 받아서, 불필요 변수와, Null값 제거.

'''
1. 입력값 json 형태로 변수화.
2. 저장소(이어하기) 옵션: reset=True(저장소 내용 지우고 초기화), reset=False(기존 csv 내용 이어서 진행((저장위치:tar_frame_save_list/[해당 folder_name])))
3. 변수(input_value)를 바꾼 후 실행 시, 이미 진행된(기존) 폴더로 이어하기 하면 변수가 불일치하여 저장안됨. 기존 저장소 폴더 및 파일을 별도 저장 후 실행바람.

# 추가.
4. 데이터는 "jsondatafile/" 폴더에 꼭 넣어야함.
5. parsing 저장 위치: "tar_frame_save_list/tar_frame.csv"
6. json 최상위 값(depth=0)만 입력.

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


# for save
reset = True # True=처음부터, False=이어하기
tar_frame_save_folder = os.getcwd() + '/tar_frame_save_list' + folder_name  ## 이어하기 옵션(reset) 저장 폴더.
tar_frame_done_txt = '/already_done_list.txt'  ## 중간 결과 진행 리스트
tar_frame_done_csv = '/tar_frame.csv'  ## 중간 결과 .csv로 저장.
tar_frame_variable_txt = '/variable.txt'  ## variable(변수) 정보를 저장.
font_size = 20

# 'bms', 'meter--ess', 'meter--grid', 'meter--load', 'meter--pv', 'pcs--ess', 'pcs--pv', 'pms', 'racks'
input_value = ['bms', 'meter--ess']



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
'''
# json depth 만큼 계산.
def search_values_name(key2_value, key):
    depth1 = []
    key_name_list = []
    if type(key2_value) is dict:
        for key3 in sorted(key2_value.keys()):
            key_name = str()
            key3_value = key2_value.get(key3)
            key_name += str(key)+'_'+str(key3)
            depthv, aa = search_values_name(key3_value, key_name)
            if depthv:
                depth1.append(depthv)
            key_name_list = key_name_list + aa
    else:
        # if key2_value:
        for i in key2_value:
            if type(i) is dict:
                for skey in sorted(i.keys()):
                    dicv = i.get(skey)
                    for k in dicv:
                        key_name_f = str(key) + '_' + str(skey)+ '_'+ str(k)
                        key_name_list = key_name_list + [key_name_f]
            else:
                key_name_f = str(key) + '_' + str(i)
                key_name_list = key_name_list + [key_name_f]
    return depth1, key_name_list
'''
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
                result_list = result_list + [None]
            if depthv:
                depth1.append(depthv)
            key_name_list = key_name_list + aa
    else:
        if key2_value:
            result_list = result_list + [key2_value]
            # print("vvvvv: ", key2_value)
            key_name_list = key_name_list + [key]
        else:
            result_list = result_list + [None]
            key_name_list = key_name_list + [key]

    return key_name_list, result_list, depth1

def get_json_values(input_value, get_value):
    print("input_value: ",input_value)
    result_depth1 = []
    keyname_list = []
    result_list = []
    for key1 in sorted(input_value.keys()):
        key_edit = str(get_value) + '_' + key1
        # print("key_edit: ",key_edit)
        key1_value = input_value.get(key1)
        # print("key1_value: ",key1_value)
        keyname, result_value, depth1 = search_values_name(key1_value, key_edit)
        # print("rrrrrrrrrr: ",result_value)
        # print("keyname: ", keyname)
        if depth1:
            result_depth1.append(depth1)
        if keyname:
            keyname_list = keyname_list + keyname
        if result_value:
            result_list = result_list + result_value

        # print("result_)list:", result_list)

    # print("result_list: ", result_list)

    return keyname_list, result_list

# keyname_list = get_values_name(input_value)

# print("keyname_list: ", keyname_list)
# print("keyname_list_len: ", len(keyname_list))

# def get_feature_ext(json_data):
#     final_name_result = []
#     final_value_result = []
#     list_name_get = []
#     target = None
#     # print(keyname_list)
#     # print(len(keyname_list))
#     for i in keyname_list:
#         list_name_get.append(i.split("_"))
#     for i in list_name_get:
#         # print(i)
#         try:
#             if len(i) == 1:
#                 target = json_data[i[0]]
#             elif len(i) == 2:
#                 target = json_data[i[0]].loc[int(i[1])]
#             elif len(i) == 3:
#                 target = json_data[i[0]].loc[int(i[1])][i[2]]
#             elif len(i) == 4:
#                 target = json_data[i[0]].loc[int(i[1])][i[2]][i[3]]
#             elif len(i) == 5:
#                 target = json_data[i[0]].loc[int(i[1])][i[2]][i[3]][i[4]]
#             elif len(i) == 6:
#                 target = json_data[i[0]].loc[int(i[1])][i[2]][i[3]][i[4]][i[5]]
#             elif len(i) == 7:
#                 target = json_data[i[0]].loc[int(i[1])][i[2]][i[3]][i[4]][i[5]][i[6]]
#             else:
#                 target = 0
#
#             # if target:
#             final_value_result = final_value_result + [target]
#             value_get_str = str()
#
#
#             for value_get in i:
#                 if value_get == i[-1]:
#                     value_get_str += str(value_get)
#                 else:
#                     value_get_str += str(value_get) + '_'
#             final_name_result.append(value_get_str)
#
#         except Exception as e:
#             '''
#             json_data['meter--grid'].loc[int(214)] -> nan 값 발생.
#             json_data['meter--grid'].loc[int(214)]['PPVphBC'] -> IndexError: invalid index to scalar variable.
#             json_data['bms'].loc[int(802)]['214']['A'] -> 214 key 값 없음.
#             '''
#             # print("SKIP ERROR VALUE")
#             # print(e)
#             # target = 0
#             pass
#
#             # final_value_result = final_value_result + [target]
#             # value_get_str = str()
#             # for value_get in i:
#             #     if value_get == i[-1]:
#             #         value_get_str += str(value_get)
#             #     else:
#             #         value_get_str += str(value_get) + '_'
#             # final_name_result.append(value_get_str)
#
#     # print("-------------=======")
#     # print("name_list: ",final_name_result)
#     # print("tar_list: ",final_value_result)
#     # print("-------------=======")
#     # print("final_value_result_len: ", len(final_value_result))
#     # print("final_name_result_len: ", len(final_name_result))
#
#     return final_name_result, final_value_result



# def make_list():  # data frame column 구성에 사용
#
#     tot_list = []
#     for td in target_device:
#         tv = target_value[td]
#         tv_list = []
#
#         # print("tv: ",tv)
#
#         for i in tv:
#             ti = target_id[i]
#             # target=json_data[td].loc[i]
#
#             ti_list = []
#             for j in range(len(ti)):
#                 # ti_list.append(ti[j])
#                 ti_list.append(td + '_' + str(i) + '_' + ti[j])
#
#             tv_list.extend(ti_list)
#         tot_list.extend(tv_list)
#     # print("tot_list: ",tot_list) # total_list
#
#     return tot_list


# # In[22]:


# def feature_ext(json_data):
#     tar_list = []
#
#     testtarget = json_data['bms'].loc[802]
#     print(testtarget['StEvtVnd']['fault'])
#
#     # target_device = ['bms','pcs--ess']
#     for td in target_device:
#         tv = target_value[td]
#         # tv = ['802','1803'], ['113']
#         tv_list = []
#         print("tv: ", tv)
#
#         for i in tv:
#             ti = target_id[i]
#             # ti = ['A','AChaMax','ADisChaMax','SoC','SoH','V'], [] ,[]
#             print("ti: ", ti)
#             # todo: td('bms'등),  loc[2번째 숫자]
#             target = json_data[td].loc[int(i)]
#
#             ti_list = []
#             # print("range: ",range(len(ti)))
#             for j in range(len(ti)):
#                 # target[ti[0]] == target[802[A]]
#                 ti_list.append(target[ti[j]])
#
#             print("ti_list: ", ti_list)
#             tv_list.extend(ti_list)
#             print("tv_list: ", tv_list)
#         tar_list.extend(tv_list)
#         print("tar_list: ", tar_list)
#     print("------------------------------24-==============================")
#     # print("tar_list: ",tar_list) # total_list
#
#     return tar_list


# In[23]:

##------------------------------------------------------------------------------------------------
## pandas 0.23 이후 버전 부터 sort=True warnming, 문제는 없는듯.
def list2pd(tar_list, df, tar_name):
    pdf = pd.DataFrame(tar_list, columns=tar_name)  # column head 수정
    pd_con = pd.concat([pdf, df['timestamp']], axis=1)

    # try:
    #     pd_con.to_csv(tar_frame_save_folder+'/tar_frame.csv', mode='a', index=False)
    # except Exception as e:
    #     return print(e)

    return pd_con


# In[24]:

# plot_title = '_'.join(target_device) + '_' + '_'.join([key for key in target_id])
plot_title = '_aaaaaaaaaa' + '_' + '_dddddddddddddddd'
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

## json파일 선택한 value의 json 값을 가져옴.
def get_select_value(jfile, select):
    data1 = pd.read_csv(jfile, names=['data', 'timestamp'])
    df1 = pd.DataFrame(data1)

    jso = dict()
    for index, row in df1.iterrows():
        date = row['data']
        jso = json.loads(date)
        jso1 = jso.get(str(select))

    jso1 = jso.get(str(select))

    return jso1

## 시행 함수.
def circle(file_name, tar_frame):


    data = pd.read_csv(file_name, names=['data', 'timestamp'])
    df = pd.DataFrame(data)

    tar_list = []
    sum_tar_value = []
    sum_tar_name = []
    kk = 0
    for each_input_value in input_value:
        for index, row in df.iterrows():
            try:
                date = row['data']
                # print("data: ",data)
                jso = json.loads(date)
                # print("jso: ",jso)
                # print("each_input_v: ", each_input_value)
                jso_v = jso.get(each_input_value)
                print(each_input_value)
                if not jso.get(each_input_value):
                    break
                if jso_v:

                    # print("jso_v: ", jso_v)
                    tar_name, get_tar_list = get_json_values(jso_v, each_input_value)
                    print("tar_name: ", tar_name)
                    print(len(tar_name))
                    # print("get_tar_list: ", get_tar_list)
                    print("tar_list: ", get_tar_list)
                    print(len(get_tar_list))
                    print("===================================================")

                    if kk == 0:
                        sum_tar_value.append(get_tar_list)
                    else:
                        sum_tar_value[index] = sum_tar_value[index] + get_tar_list
                        print("sum_tar_val: ",len(sum_tar_value))

                    if index == 0:
                        sum_tar_name.extend(tar_name)
                else:
                    get_tar_list = [None]
                    if kk == 0:
                        sum_tar_value.append(get_tar_list)
                    else:
                        sum_tar_value[index] = sum_tar_value[index] + get_tar_list

            except ValueError:
                pass

        kk += 1

    print("22222222222222222222222:",sum_tar_name)
    print(len(sum_tar_name))
    print("sum_tar_value: ",sum_tar_value)
    print(len(sum_tar_value))
    print(len(sum_tar_value[0]))


    for value in sum_tar_value:
        tar_list.append(value)


    try:
        print('--------------------5--------------------')
        print(type(tar_list))

        tar_box_to_save = (list2pd(tar_list, df, sum_tar_name)).reset_index(drop=True)
        # tar_box_to_save = (list2pd(get_tot_list, tar_list, df))
        print('--------------------6--------------------')
        if variable_check(input_value) == True:
            print('--------------------7--------------------')
            tar_save(tar_box_to_save, input_value)
            print('--------------------8--------------------')
            tar_frame = tar_frame.append(tar_box_to_save)
            print('--------------------9--------------------')
            file_save(file_name)
        else:
            return False

    except Exception as e:
        print("------44444-------------")
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




