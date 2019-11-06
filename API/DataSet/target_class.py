#-*- coding:utf-8 -*-
# 1. 인수량(insu) or 검칭량(sub) 선택.
# 2. [광주, 나주, 장성, 담양] 다중선택.

'''general'''
import pandas as pd
import json
'''library'''
'''directory'''
## database
from DB.DataBase.database import db_session
from DB.DataBase.models import Login, TestTable
from DB.DataBase.database import dbsearch

class Data_get_from_db(object):

    _predicTarget = str  ## 예측 대상(insu, sub)
    _predicArea = str  ## 선택한 지역들(s).

    def __init__(self, select, tableName, condition):
        self._select = select  ## 보고 싶은 지역 정보 선택.
        self._tableName = tableName  ## 정보가 들어있는 테이블
        self._condition = condition  ## 조건문(원하는 정보만 get) , ex) 20190501 이후.


    # 최종 결과 - 조건절 포함.
    def final_result_where(self):

        self.get_select_field(self._select)
        rselect = "select " + str(self._selectArea)
        # print(rselect)
        rfrom = " from " + str(self._tableName)
        # print(rfrom)
        self.get_where_item2(**self._condition)
        rwhere = " where " + str(self._areaValues)
        rresult = rselect + rfrom + rwhere
        return rresult
