# -*- coding: utf-8 -*-
from DB.DataBase.database import db_session, dbsearch, dbsearch1
from flask import Blueprint, jsonify, send_from_directory, abort, session, send_file
from flask import make_response, request, current_app, Response
from DB.DataBase.models import ModelTable, ResourceTable, LocationTable, DataTable, SmartcityTable
from API.api_helper.api_helper import response_json_value, response_json_list, post_request
import json


model_apis = Blueprint('model_apis', __name__, url_prefix='/api')

@model_apis.route('/models', methods=['GET'])
def model_get():
    try:
        query = "select * from model ORDER BY key"
        records = db_session.execute(query)
        result = []
        for i in records:
            # print(i)
            result_dict = dict()
            for x, y in i.items():
                result_dict.update({x: y})
            # print(result_dict)

            result.append(result_dict)

        return response_json_list(result)
    except:
        return jsonify(False)

@model_apis.route('/models/<int:key>', methods=['GET'])
def model_get_detail(key):
    try:
        query = "select * from model WHERE key =%d" % (key)
        records = db_session.execute(query)
        result = []
        for i in records:
            # print(i)
            result_dict = dict()
            for x, y in i.items():
                result_dict.update({x: y})
            # print(result_dict)

            result.append(result_dict)

        return response_json_value(result)
    except Exception as e:
        abort(400)


'''
{
  "id":"daily",
  "name":"일간예측"
}
{
  "id":"monthly1",
  "name":"월간예측 과거12개월"
}
{
  "id":"monthly2",
  "name":"월간예측 미래24개월"
}
{
  "id":"yearly",
  "name":"년간예측 미래5년"
}
'''
@model_apis.route('/models', methods=['POST'])
def model_post():
    try:
        req = request.get_json()
        jsonString = json.dumps(req)
        data = json.loads(jsonString)

        model_id = data['id']
        model_name = data['name']

        db_session.add(ModelTable(id=model_id, name=model_name))
        db_session.commit()

        return jsonify(True)
    except Exception as e:
        print(e)
        abort(400)



@model_apis.route('/models/<int:key>', methods=['PUT'])
def model_put(key):
    try:
        req = request.get_json()
        jsonString = json.dumps(req)
        data = json.loads(jsonString)

        model_id = data['id']
        model_name = data['name']

        value = db_session.query(ModelTable).get(key)
        value.id = model_id
        value.name = model_name
        db_session.commit()
        return jsonify(True)

    except Exception as e:
        print(e)
        abort(400)



@model_apis.route('/models/<int:key>', methods=['DELETE'])
def model_delete(key):
    try:
        db_session.query(ModelTable).filter(ModelTable.key == key).delete()
        db_session.commit()
        return jsonify(True)
    except:
        return jsonify(False)


######################### resource #################################################################

# @model_apis.route('/resources', methods=['GET'])
# def resource_get():
#     try:
#         query = "select * from resource ORDER BY key"
#         records = db_session.execute(query)
#         result = []
#         for i in records:
#             # print(i)
#             result_dict = dict()
#             for x, y in i.items():
#                 result_dict.update({x: y})
#             # print(result_dict)
#
#             result.append(result_dict)
#
#         return response_json_list(result)
#     except:
#         return jsonify(False)

@model_apis.route('/resources', methods=['GET'])
def resource_get():
    try:
        query = "select * from resource ORDER BY key"
        records = db_session.execute(query)
        result1 = []
        result2 = []
        result3 = []
        for i in records:
            # print(i)
            result_dict = dict()
            for x, y in i.items():
                result_dict.update({x: y})
            # print(result_dict)

            if '.' in result_dict.get('id'):
                # print(result_dict.get('id'))
                result1.append(result_dict)

            elif 'static/' in result_dict.get('id'):
                # print(result_dict.get('id'))
                result2.append(result_dict)
            else:
                result3.append(result_dict)

            # print(result_dict)

        final_result = {"hygas": result1,"statics": result2, "other": result3}

        return jsonify(final_result)

        # return response_json_list(result)
    except:
        return jsonify(False)

@model_apis.route('/resources/<int:key>', methods=['GET'])
def resource_get_detail(key):
    try:
        query = "select * from resource WHERE key =%d" % (key)
        records = db_session.execute(query)
        result = []
        for i in records:
            # print(i)
            result_dict = dict()
            for x, y in i.items():
                result_dict.update({x: y})
            # print(result_dict)

            result.append(result_dict)

        return response_json_value(result)
    except Exception as e:
        abort(400)


'''
{
  "id":"3303.0",
  "name":"temp",
  "explain":"온도(IoT 온습도센서, 온도 측정값)"
}
{
  "id":"30001.1",
  "name":"insu",
  "explain":"가스인수량(원격검침 가스 인수량)"
}
{
  "id":"30001.2",
  "name":"insu",
  "explain":"가스검침량(원격검침 가스 검침량)"
}
{
  "id":"30005.0",
  "name":"sub",
  "explain":"인원수(해양에너지 가입자수)"
}
'''
@model_apis.route('/resources', methods=['POST'])
def resource_post():
    try:
        req = request.get_json()
        jsonString = json.dumps(req)
        data = json.loads(jsonString)

        resource_id = data['id']
        resource_name = data['name']
        resource_explain = data['explain']

        db_session.add(ResourceTable(id=resource_id, name=resource_name, explain=resource_explain))
        db_session.commit()

        return jsonify(True)
    except Exception as e:
        print(e)
        abort(400)


## 스마트 시티 static API insert 기능.
@model_apis.route('/resource/statics', methods=['POST'])
def smartCity_datasetlist():
    dlist = [name for name in dbsearch1.table_names() if name.startswith('dataset_')]
    result = list()
    for i in dlist:
        name = i.replace("dataset_", "")
        static_name = "static/%s" % (name)
        result.append(static_name)
        try:
            db_session.add(ResourceTable(id=static_name, name=name))
            db_session.commit()
        except Exception as e:
            print(e)
            pass

    return jsonify({"resources": result})

@model_apis.route('/resources/<int:key>', methods=['PUT'])
def resource_put(key):
    try:
        req = request.get_json()
        jsonString = json.dumps(req)
        data = json.loads(jsonString)

        resource_id = data['id']
        resource_name = data['name']
        resource_explain = data['explain']

        value = db_session.query(ResourceTable).get(key)
        value.id = resource_id
        value.name = resource_name
        value.explain = resource_explain
        db_session.commit()
        return jsonify(True)

    except Exception as e:
        print(e)
        abort(400)



@model_apis.route('/resources/<int:key>', methods=['DELETE'])
def resource_delete(key):
    try:
        db_session.query(ResourceTable).filter(ResourceTable.key == key).delete()
        db_session.commit()
        return jsonify(True)
    except:
        return jsonify(False)



#---------------------------------------------------------------------

@model_apis.route('/locations', methods=['GET'])
def datasets_locations_get():
    query = "select * from location ORDER BY key"
    records = db_session.execute(query)
    # location_list = ["gwangju", "naju", "jangsung", "damyang"]

    result = []
    for i in records:
        result.append(dict(i))

    return response_json_list(result)

@model_apis.route('/locations/<int:key>', methods=['GET'])
def datasets_locations_get_key(key):
    query = "select * from location where key=%d"%(key)
    records = db_session.execute(query)
    # location_list = ["gwangju", "naju", "jangsung", "damyang"]

    result = []
    for i in records:
        result.append(dict(i))

    return response_json_value(result)
'''
{
  "id": "naju",
  "name":"나주",
  "name_en":"Naju"
}
{
  "id": "gwangju",
  "name":"광주",
  "name_en":"Gwangju"
}
{
  "id": "jangsung",
  "name":"장성",
  "name_en":"Jangsung"
}
{
  "id": "damyang",
  "name":"담양",
  "name_en":"Damyang"
}
'''
@model_apis.route('/locations', methods=['POST'])
def datasets_locations_post():
    try:
        data = post_request()
        ## id, name, name_en

        id = data['id']
        try:
            name = data['name']
        except:
            name = None

        try:
            name_en = data['name_en']
        except:
            name_en = None

        db_session.add(LocationTable(id=id, name=name, name_en=name_en))
        db_session.commit()

        return jsonify(True)

    except:
        return jsonify(False)

@model_apis.route('/locations/<int:key>', methods=['DELETE'])
def datasets_locations_delete(key):
    try:
        db_session.query(LocationTable).filter(LocationTable.key == key).delete()
        db_session.commit()
        return jsonify(True)
    except:
        return jsonify(False)

@model_apis.route('/locations/<int:key>', methods=['PUT'])
def datasets_locations_put(key):
    try:
        data = post_request()
        ## id, name, name_en

        id = data['id']

        try:
            name = data['name']
        except:
            name = None

        try:
            name_en = data['name_en']
        except:
            name_en = None

        value = db_session.query(LocationTable).get(key)
        value.id = id
        value.name = name
        value.name_en = name_en
        db_session.commit()
        return jsonify(True)

    except:
        return jsonify(False)


## 스마트시티 따로 ############
'''
{
		"icon" : "age",
		"title": "연령대 별 소비",
		"path" : "cjr-spend-age"
}

'''

@model_apis.route('/datasets/statics', methods=['POST'])
def datasets_statc_post():
    try:
        data = post_request()
        ## id, name, name_en

        if isinstance(data, list):
            for i in data:
                path = i['path']

                try:
                    title = i['title']
                except:
                    title = None

                try:
                    icon = i['icon']
                except:
                    icon = None

                db_session.add(SmartcityTable(icon=icon, title=title, path=path))
                db_session.commit()
        else:

            path = data['path']

            try:
                title = data['title']
            except:
                title = None

            try:
                icon = data['icon']
            except:
                icon = None

            db_session.add(SmartcityTable(icon=icon, title=title, path=path))
            db_session.commit()
        return jsonify(True)

    except:
        return jsonify(False)

@model_apis.route('/datasets/statics', methods=['GET'])
def datasets_statc_get():
    query = "select * from smartcity ORDER BY key"
    records = db_session.execute(query)
    # location_list = ["gwangju", "naju", "jangsung", "damyang"]

    result = []
    for i in records:
        result.append(dict(i))

    return response_json_list(result)

@model_apis.route('/datasets/statics/<int:key>', methods=['GET'])
def datasets_statc_get_key(key):
    try:
        query = "select * from smartcity where key=%d" % (key)
        records = db_session.execute(query)
        # location_list = ["gwangju", "naju", "jangsung", "damyang"]

        result = []
        for i in records:
            result.append(dict(i))

        return response_json_value(result)
    except:
        return abort(400)

@model_apis.route('/datasets/statics/<int:key>', methods=['DELETE'])
def datasets_static_delete(key):
    try:
        db_session.query(SmartcityTable).filter(SmartcityTable.key == key).delete()
        db_session.commit()
        return jsonify(True)
    except:
        return jsonify(False)

@model_apis.route('/datasets/statics/<int:key>', methods=['PUT'])
def datasets_static_put(key):
    try:
        data = post_request()
        path = data['path']

        try:
            title = data['title']
        except:
            title = None

        try:
            icon = data['icon']
        except:
            icon = None

        value = db_session.query(SmartcityTable).get(key)
        value.path = path
        value.title = title
        value.icon = icon
        db_session.commit()
        return jsonify(True)

    except:
        return jsonify(False)

