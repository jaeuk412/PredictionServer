# -*- coding: utf-8 -*-

import json
import os


from flask import Blueprint, jsonify, send_from_directory, abort, session, send_file
from flask import make_response, request, current_app, Response
from datetime import timedelta, datetime
from functools import update_wrapper
from DB.DataBase.database import db_session
from DB.DataBase.models import Login
from six import string_types




# request로 웹에서 보낸 json형태 받음.
def post_request():
    req = request.get_json()
    jsonString = json.dumps(req)
    data = json.loads(jsonString)
    return data

# db를 딕셔너리 값으로.
def records_to_array(records):
    return [dict(record) for record in records]

# db 레코드 형태의 출력 값을 리스트 안의 json 형태로 만듬.
def response_json_list(records):
    return jsonify(records_to_array(records))

# db 레코드 형태의 출력 값을 단일 json 형태로 만듬.
def response_json_value(records):
    return jsonify(records_to_array(records)[0])

# 해당 쿼리에 해당하는 DB key를 받아옴.
def get_query_key(query):
    result = db_session.execute(query)
    print("result: ", result)
    targets = []
    for k in result:
        targets.append(dict(k))

    print("targets: ",targets)
    # DB의 key 값을 가져 온다.
    d_key = targets[0].values()
    for i in d_key:
        return i

def file_remove(path):
    if os.path.isfile(path):
        os.remove(path)
    else:
        pass

def date_time(dt):
    start_date = int(dt.strftime('%Y%m%d'))
    start_year = dt.year
    start_month = dt.month
    start_day = dt.day
    return start_date, start_year, start_month, start_day

def devide_date(date):
    # print("date: ",date)
    start_date = str(date)
    start_year = int(start_date[0:4])
    start_month = int(start_date[4:6])
    start_day = int(start_date[6:8])
    return start_year, start_month, start_day

def get_user_pkey():
    try:
        key = session['logger']
        pkey = db_session.query(Login.pkey).filter(Login.id == str(key))
        login = db_session.query(Login).get(pkey)
    except:
        pkey = 0
    else:
        pkey = login.pkey

    return pkey

## 3.5에 맞게 수정.
def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):

    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    # if headers is not None and not isinstance(headers, basestring):
    if headers is not None and not isinstance(headers, string_types):
        headers = ', '.join(x.upper() for x in headers)
    # if not isinstance(origin, basestring):
    if not isinstance(origin, string_types):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            try:
                origin_value = request.headers['Origin']
            except:
                origin_value = None

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin_value
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            h['Access-Control-Allow-Credentials'] = 'true'
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

class get_query_string():

    def __init__(self):
        return

    def getInt(self, key):
        return request.args.get(key, type=int)

    def getStr(self, key):
        return request.args.get(key, type=str)

