# -*- coding: utf-8 -*-
# 유저 로그인. 로그아웃,

'''general'''
import json
'''library'''
## flask(REST-API)
from flask import Blueprint, jsonify, send_from_directory, abort, session, send_file
from flask import make_response, request, current_app, Response
from sqlalchemy import func
##  check format of data
import wtforms_json
from wtforms import Form, StringField, IntegerField
from wtforms.validators import InputRequired
'''directory'''
## database
from DB.DataBase.database import db_session
from DB.DataBase.models import Login
from DB.DataBase.database import dbsearch1
## api helper
from API.api_helper.api_helper import crossdomain
from API.api_helper.api_helper import post_request, response_json_list, response_json_value
''' '''

user_apis = Blueprint('user_apis', __name__, url_prefix='/api')

wtforms_json.init()

@user_apis.route('/users/<int:userid>/level', methods=['POST'])
def api_login(userid):
    # login_level = AuthLevelForm.from_json(request.json)
    req = request.get_json()
    jsonString = json.dumps(req)
    data = json.loads(jsonString)

    login_level = data['level']
    user = db_session.query(Login).get(str(userid))
    user.level = login_level.level.data
    db_session.commit()

    return jsonify(True)


@user_apis.route('/auth/check', methods=['GET'])
def user_check():
    # print session
    return jsonify(dict(session))

'''
{
  "id":"admin",
  "password":"iot2019"
}
'''
@user_apis.route('/auth/login', methods=['POST'])
@crossdomain(origin='*')
def api_auth_login():
    # print("---------0------------")
    # userName = request.args.get('name', type=str)
    # userPw = request.args.get('pw', type=str)

    # form = LoginForm.from_json(request.json)
    req = request.get_json()
    jsonString = json.dumps(req)
    data = json.loads(jsonString)

    userId = data['id']
    userPw = data['password']
    # print(userId)
    # print(userPw)

    if userId:
        # print("userid: ",userId)

        try:
            pkey = db_session.query(Login.pkey).filter(Login.id == str(userId))
            login = db_session.query(Login).get(pkey)
            userpkey = login.pkey
            # print("userpkey: ", userpkey)
        except Exception as e:
            return jsonify(False)

        else:

            if userpkey:
                # print(userPw)
                # print(userpkey)
                # print(type(userpkey))

                query = "select * from login where pkey=%d"%(userpkey)
                query = db_session.execute(query)

                ## db_session.query(Login).filter(Login.pkey == userpkey)

                records = []
                for row in query:
                    records.append(dict(row))
                # print("======================")
                # print("records: ",records)
                # print(login.password)
                # print(userPw)
                if userPw:
                    if login.password == userPw:
                        session['logger'] = userId
                        return response_json_value(records)
                    else:
                        return jsonify(False)
                else:

                    abort(400)

            else:
                if userPw:
                    return jsonify(False)

                else:
                    # print('--------1------------')
                    return abort(400)
    else:
        # print('--------2------------')
        abort(400)


#로그아웃
@user_apis.route('/auth/logout', methods=['GET', 'POST'])
@crossdomain(origin='*')
def api_auth_logout():
    # form = LoginForm.from_json(request.json)

    req = request.get_json()
    jsonString = json.dumps(req)
    data = json.loads(jsonString)

    try:
        userName = data['id']
    except:
        abort(400)

    if userName:

        userno = db_session.query(Login.pkey).filter(Login.id == userName).all()

        if userno:
            userno = userno[0]
            userno = userno[0]

            user = db_session.query(Login).get(userno)

            if user.id == userName:
                session.pop('logger')

                # for key in session.keys():
                #     session.pop(key)

                return jsonify(True)

            else:
                return jsonify(False)

        else:
            return jsonify(False)

    else:
        for i in session:
            session.pop(i)

'''
{
  "id":"admin",
}
'''
@user_apis.route('/auth/restore', methods=['POST'])
@crossdomain(origin='*')
def api_auth_restore():
    # restore_key = session['logger']

    # form = LoginForm.from_json(request.json)

    req = request.get_json()
    jsonString = json.dumps(req)
    data = json.loads(jsonString)

    userName = data['id']
    # print(userName)
    # print(session)

    try:
        key = session['logger']
        # print(key)

        ## 서버 session 하고 웹 session(userName)을 비교.
        if key == userName:

            ## DB 저장된 user 아이디 불러와서 비교.
            userno = db_session.query(Login.pkey).filter(Login.id == userName).all()

            if userno:
                userno = userno[0]
                userno = userno[0]

                query = "select * from login where pkey=%s"%(userno)
                query = db_session.execute(query)
                ##db_session.query(Login).filter(Login.pkey == userno)
                records = []
                for row in query:
                    records.append(dict(row))

                user = db_session.query(Login).get(userno)

                if user.id == userName:
                    return jsonify(records[0])

                else:
                    # print('3')
                    return jsonify(False)

            else:
                # print('2')
                return jsonify(False)

        else:
            # print('1')
            return jsonify(False)

    except:
        # print('except')
        return jsonify(False)



@user_apis.route('/users', methods=['GET'])
@crossdomain(origin='*')
def api_users():
    # print session
    # query = db_session.query(Login).order_by(Login.id.asc())
    query = "select * from login ORDER BY pkey"
    records = db_session.execute(query)

    count = db_session.query(func.count('*')).select_from(Login).scalar()
    print(count)


    result=[]
    for i in records:
        result.append(dict(i))

    fresult = {"data":result,"total":count}
    return jsonify(fresult)


@user_apis.route('/users/<int:userid>', methods=['GET'])
@crossdomain(origin='*')
def api_usersid(userid):
    # query = db_session.query(Login).filter(Login.id == str(userid))
    query = "select * from login where id=%s"%(userid)
    result = db_session.execute(query)

    rect = []

    for row in result:
        rect.append(row)

    # dict1 = [dict(record) for record in rect]

    return response_json_value(rect)


@user_apis.route('/users', methods=['POST'])
@crossdomain(origin='*')
def api_userAdd():
    # form = LoginForm.from_json(request.json)

    req = request.get_json()
    jsonString = json.dumps(req)
    data = json.loads(jsonString)

    try:
        id = data['id']
        pw = data['password']

        db_session.add(Login(id=id, password=pw))
        db_session.commit()

        return jsonify(True)
    except:
        abort(400)




        # print(e)
        # db_session.rollback()



@user_apis.route('/users/<int:userid>', methods=['PUT'])
@crossdomain(origin='*')
def api_useredit(userid):
    req = request.get_json()
    jsonString = json.dumps(req)
    data = json.loads(jsonString)

    try:
        # form = LoginForm.from_json(request.json)

        id = data['id']
        pw = data['password']


        pkey = db_session.query(Login.pkey).filter(Login.id == str(userid))
        login = db_session.query(Login).get(pkey)

        login.id = id
        login.password = pw
        db_session.commit()

        return jsonify(True)

    except Exception as e:
        print(e)
        abort(400)


@user_apis.route('/users/<int:userid>/exists', methods=['GET'])
@crossdomain(origin='*')
def api_userexist(userid):

    try:
        query = db_session.query(Login).filter(Login.id == str(userid))
        result = db_session.execute(query)

        rect = []
        for row in result:
            rect.append(row)

        if not rect:
            return jsonify(False)
        else:
            return response_json_value(rect)

    except Exception as e:
        print(e)
        return jsonify(False)



@user_apis.route('/users/<int:userid>', methods=['DELETE'])
def api_userDel(userid):
    pkey = db_session.query(Login.pkey).filter(Login.id == str(userid))
    login = db_session.query(Login).get(pkey)

    print(login.pkey)

    if login.id == str(userid):
        db_session.query(Login).filter(Login.pkey == login.pkey).delete()
        db_session.commit()
        return jsonify(True)
    else:
        return jsonify(False)





# class AuthLevelForm(Form):
#     level = IntegerField('level', [InputRequired])
#
#
# class LoginForm(Form):
#     id = StringField('id', [InputRequired()])
#     pw = StringField('password', [InputRequired()])