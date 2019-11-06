# import sys
#
# sys.path.append('/home/uk/machbase_home/3rd-party/python3-module/machbaseAPI-1.0')
# from machbaseAPI.machbaseAPI import machbase
# import json
#
# def connect():
#     db = machbase()
#     if db.open('127.0.0.1','SYS','MANAGER',5656) is 0 :
#         return db.result()
#     # if db.execute('select count(*) from m$tables') is 0 :
#     #     return db.result()
#     result = db.result()
#     if db.close() is 0 :
#         return db.result()
#     return result
#

'''
machadmin --help

machadmin
machadmin -c

'''

from machbase.machbaseAPI.machbasea import machbase

def connect():
    db = machbase()
    if db.open('127.0.0.1','SYS','MANAGER',5656) is 0 :
        return db.result()

    if db.execute('select count(*) from m$tables') is 0 :
        return db.result()

    result = db.result()

    if db.close() is 0 :
        return db.result()

    return result

if __name__=="__main__":
    print(connect())