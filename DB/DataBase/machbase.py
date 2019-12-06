#-*- coding:utf-8 -*-
#******************************************************************************
# Copyright of this product 2013-2023,
# MACHBASE Corporation(or Inc.) or its subsidiaries.
# All Rights reserved.
#******************************************************************************

# $Id:$
'''
## 접속
$machadmin -u
## 쿼리창으로 이동
$machsql
## 테그 테이블 생성
$create tagdata table TAG (name varchar(20) primary key, time datetime basetime, value double summarized);
## Tag metadata를 생성 후, 해당 테크로 insert 해주더라.
## (metadata 생성이 tag_table의 key에 해당하고, 이 key가 없이는 insert 못함.)
#TAG_0001이라는 이름에 대한, metadata(key) 생성
$insert into tag metadata values ('TAG_0001');
## 아마 이 key가 에트리의 "HYGAS.NAJU_C_HOUSE.30001.1" 를 나타내는거 같음. (밑에내용수정)
# 한개씩.
$insert into tag values('TAG_0001', now, 0);
$insert into tag values('TAG_0001', now, 1);
$insert into tag values('TAG_0001', now, 2);
## insert의 2번째인 time 값에 'now' 말고 "2019-11-11 11:11:11"로 넣으니 잘 들어감.
## "HYGAS.NAJU_C_HOUSE.30001.1"(len=26) 로 메타데이터 만들었는데 'HYGAS.NAJU_C_HOUSE.3' 까지 밖에 못들어감(len=20), 크기 제한이 있는듯.
### 근데 에트리 준 java 코드 보니까 풀네임(HYGAS.NAJU_C_HOUSE.30001.1)으로 TAG name(key)를 만듬.. TAG 처음 선언에서 이름을 20으로 제한한게 문제였음.
### 테크 테이블은 1개 밖에 생성이 안되는거 같다.
## tag table 지우고 다시함.
$drop table tag;
## name varchar(40)으로.
$create tagdata table TAG (name varchar(40) primary key, time datetime basetime, value double summarized);
$insert into tag metadata values ('HYGAS.NAJU_C_HOUSE.30001.1');
$insert into tag values('HYGAS.NAJU_C_HOUSE.30001.1', now, 44);
## 잘 된다. python execute 문에서도 잘 실행 된다.

### 값 insert 후에 바로 select 하면 insert한 값이 바로 출력 안 됨.
### insert, select 사이에 sleep(1)를 두니 출력이 됐음.(sleep 0.01까지됨, 0.001은 안됨)(0.01도 데이터 25개 되니까 안됨, 0.02는 됨)
## 데이터 1개인데도 저장하는데 시간이 좀 드는듯. 처음 접속 때문에 그럴지도.
### 계속 해봤는데 sleep(0.1)이 나을듯, 데이터 35개 이상부터 이상하게 다시 안된다. sleep 0.05까지 해도 안됨.


'''

import json
from machbaseAPI.machbaseAPI import machbase
import time
import timeit
start = timeit.default_timer()

def connect(query):
    db = machbase()
    # if db.open('122.128.78.203', 'sys', 'zhaortm0852db', 5656) is 0:
    ## 해당 접속 정보가 없으면 없다고 리턴.
    if db.open('127.0.0.1','SYS','MANAGER',5656) is 0 :
        return db.result()

    ## SELECT * FROM tag where name='HYGAS.NAJU_C_HOUSE.30001.1'
    ## SELECT * FROM tag
    ## insert into tag values('HYGAS.NAJU_C_HOUSE.30001.1', now, 44)
    # if db.execute('select count(*) from m$tables') is 0 :
    if db.execute(query) is 0:
        return db.result()

    result = db.result()

    if db.close() is 0 :
        return db.result()

    ## machbase에 있는 값을 불러오니 dictionary 형태들이 이어진 str형태 였다.
    ## 연결 부위에 특수기호를 넣어서 개별로 나눴고,
    splitdata = result.replace('},{', '}*#$*{').split('*#$*')

    ## 각 개별에 대해서 dictionary화 하였다.
    dictvalue = []
    for i in splitdata:
        dictvalue.append(json.loads(i))

    return dictvalue

'''
house houseCooking    houseJHeating     houseCHeating   salesOne   salesTwo   bizHeating   bizCooling   industry   heatFacility  heatCombined  cNG
HOUSE, HOUSE-COOKING, HOUSE-J-HEATING, HOUSE-C-HEATING, SALES-ONE, SALES-TWO, BIZ-HEATING, BIZ-COOLING, INDUSTRY, HEAT-FACILITY, HEAT-COMBINED, CNG
단독주택, 취사전용, 공동난방, 중앙난방, 영업1종, 영업2종, 업무용난방, 업무용냉방, 산업용, 열전용설비, 열병합발전, CNG
## 단독주택 가스인수량(insu) insert into tag metadata values ('HYGAS.NAJU_C_HOUSE.30001.1'); (각 12개 니까 x 12)
## 단독주택 가스검침량 insert into tag metadata values ('HYGAS.NAJU_C_HOUSE.30001.2'); (각 12개 니까 x 12)
## 온도(tmp) ~ (3303.0)
## 인원수(sub) ~ (30005.0)
## csv를 읽어서 저장하는게 machbase에 있다고함. 연습해봐야 할듯.
$csvimport -t TAG -d data.csv -F "time YYYY-MM-DD HH24:MI:SS mmm:uuu:nnn" -l error.log

'''

##---------------------------------------------------------------------------------------------------------
## todo: 마크베이스에 저장 할 때
final_value_list = list()
folder_path = '/home/uk/PredictionServer/prediction/'
area = 'naju'
resource = 'insu' # or '30001.1
ddstart=2015

path = folder_path + 'data/insu/%s_insu_%d' % (area.lower(), ddstart)
# print("path: ",path)

with open(path, 'r') as f:
    dataname_get = f.readlines()

# print("dataname_get: ",dataname_get)
# date_name = dataname_get[0].replace('\t', ' ').split(' ')
# print("date_name: ", date_name)


mach_usekind = list()
resource_value = str()

# todo: csv 파일 컬럼은 반듯이 년, 월, 일, house ...로 *년,월,일 꼭 있어야함*
count=0
for ii in dataname_get:
    if count == 0:
        date_name = ii.replace('\t', ' ').split(' ')
        for i in date_name:
            if '_' in i:
                ## strip = 뒤 \n 제거
                i = i.split('_')[1].strip().upper()

                # print(resource)
                # print(mach_usekind)
            mach_usekind.append(i)

        ## 년/원/일 을 제외한 뒤에 나머지 컬럼명을 가져옴.
        mach_usekind = mach_usekind[3:]
        # print(mach_usekind)


        if resource == 'insu':
            resource_value = '30001.1'
        else:
            resource_value = '30001.2'

        try:
            ## insert into tag metadata values ('TAG_0001');
            for t in mach_usekind:
                query="insert into tag metadata values ('HYGAS.%s_C_%s.%s')"%(area.upper(), t, resource_value)
                # print(query)
                # dblist = connect(query)
                # print(dblist)
        except:
            pass

    else:
        k=0
        for usekind in mach_usekind:

            date = ii.replace('\t', ' ').split(' ')[0:3]
            date_value = '%d-%02d-%02d' % (int(date[0]), int(date[1]), int(date[2]))
            # print(date_value)

            ## 3~14 (12걔)
            value = ii.replace('\t', ' ').split(' ')[3 + k]
            # print(value)
            query1 = "insert into tag values('HYGAS.%s_C_%s.%s', '%s', %d)" % (area.upper(), usekind, resource_value, date_value, int(value))
            # print(query1)
            # dblist2 = connect(query1)
            # print(dblist2)
            k += 1

    count += 1


# print(final_value_list)
##---------------------------------------------------------------------------------------------------------

# for i in range(1):
#     # kk = 98.3
#     # query1 = "insert into tag values('HYGAS.NAJU_C_HOUSE.30001.1', '2019-11-28 09:43:25', %f)"%(kk)
#     query1 = "insert into tag values('HYGAS.NAJU_C_SUM.30001.1', now, 149105)"
#     dblist2 = connect(query1)
#     print(dblist2)

# time.sleep(0.1)
#
# ## todo: 마크베이스에서 불러 올때
# query = "SELECT * FROM tag "
# dblist = connect(query)
# # print(dblist)
#
# k = 0
# value_name = list()
# final_value=[]
# for row_n in dblist:
#     # print(row_n)
#     # print(type(row_n))
#
#     row_n['VALUE']=float(row_n.get('VALUE'))
#     # dict_value={}
#     middle_value = []
#     for x, y in row_n.items():
#         if k == 0:
#             value_name.append(x)
#         # dict_value.update({x:y})
#         middle_value.extend([y])
#     final_value.append(middle_value)
#     k += 1
#
# final_value.insert(0,value_name)
# # print(value_name)
# # print(final_value)
#
#
# stop = timeit.default_timer()
# # print("exe-time: ", stop - start)
