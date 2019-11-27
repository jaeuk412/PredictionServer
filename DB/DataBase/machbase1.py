#-*- coding:utf-8 -*-

import json
from machbaseAPI.machbaseAPI import machbase

class machbasedb(object):

    db = machbase()

    def __init__(self):
        pass
        # self._request=request

    def connect(self, a, b, c, d):
        # if db.open('122.128.78.203', 'sys', 'zhaortm0852db', 5656) is 0:
        ## 해당 접속 정보가 없으면 없다고 리턴.
        if self.db.open(a, b, c, d) is 0:
            return self.db.result()

        ## SELECT * FROM tag where name='HYGAS.NAJU_C_HOUSE.30001.1'
        ## SELECT * FROM tag
        ## insert into tag values('HYGAS.NAJU_C_HOUSE.30001.1', now, 44)
        # if db.execute('select count(*) from m$tables') is 0 :

        result = self.db.result()

        if self.db.close() is 0:
            return self.db.result()

        return result


    def execueaa(self, query):
        if self.db.execute(query) is 0:
            return self.db.result()






query = "SELECT * FROM tag where name='HYGAS.NAJU_C_HOUSE.30001.1'"

dbdb = machbasedb()
dblist = dbdb.connect('127.0.0.1','SYS','MANAGER',5656)
dbprin = dbdb.execueaa(query)

# kk = dblist.execute(query)
# print(kk.result())


for row_n in dbprin.result():
    for x, y in row_n.items():
        print(y)
