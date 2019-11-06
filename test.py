import json
import pandas as pd
from DB.DataBase.database import dbsearch1
from DB.DataBase.database import db_session
# obj="""{
#     "name" : {"asdad":{"wwwe":"wewe","123":{"22":"33","32":{"22":"555"}}}}
# }"""
#
# result = json.loads(obj)
# print(result)
# print(type(result))
#
# key = result.keys()
# print(key)
#
# for i in key:
#     value = result.get(i)
#     print(value)
#     result_df = pd.DataFrame(value["asdad"])
#     print(result_df)
#
# # result_df = pd.DataFrame(result,columns=['name' ,'age', 'gender', 'address'])

query = "select * from 'GWANJUCHALLENGE_acc_inflow'"
records1 = dbsearch1.execute(query)

# recn = []
# for row_n in records1:
#     recn.append(dict(row_n))
#
# print(recn)