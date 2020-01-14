# -*- coding: utf-8 -*-

# general
import datetime
import re

# library
from flask import Flask, send_from_directory, make_response, url_for, redirect
from flask_sse import sse

# directory
from DB.DataBase.database import create_tables, db_session
from DB.DataBase.models import DataTable
from API.api_helper.api_helper import crossdomain


from API.api_helper.user_directory import ip_path
# from flask_cors import CORS
# from celery import Celery
#
# def make_celery(app):
#     celery = Celery(
#         app.import_name,
#         backend=app.config['CELERY_RESULT_BACKEND'],
#         broker=app.config['CELERY_BROKER_URL']
#     )
#     celery.conf.update(app.config)
#
#     class ContextTask(celery.Task):
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return self.run(*args, **kwargs)
#
#     celery.Task = ContextTask
#     return celery


app = Flask(__name__)

# CORS(app, supports_credentials=True)
# CORS(app)
# app.config['CORS_HEADERS'] = 'Content-Type'

# ## celery
# app.config.update(
#     CELERY_BROKER_URL='redis://localhost:6379',
#     CELERY_RESULT_BACKEND='redis://localhost:6379'
# )
app.config["REDIS_URL"] = "redis://localhost"

app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
app.config['SESSION_COOKIE_AGE'] = 1500
app.config['MAX_CONTENT_LENGTH'] = 200000
app.permanent_session_lifetime = datetime.timedelta(days=1)

# https://stackoverflow.com/questions/37325505/how-to-rewrite-static-url-about-flask
app.url_map._rules.clear()
app.url_map._rules_by_endpoint.clear()
# app.url_map.host_matching = True
# app.add_url_rule(app.static_url_path + '/<path:filename>',
#                  endpoint='static',
#                  view_func=app.send_static_file,
#                  host='0.0.0.0')
# with app.test_request_context():
#     print(url_for('static', filename='index', _external=True))

# print(app)
# CSRF_ENABLED = True
# CSRF_SESSION_KEY = "secret"
# SECRET_KEY = "secret"
# celery = make_celery(app)
webapp_path = 'static'
webapp_index = 'index.html'

redirect("0.0.0.0", code=392)
## 웹페이지 시작.
@app.after_request
## origin=ip_path는 해당 컴터
@crossdomain(origin='*', headers='content-type')
def app_global_headers(response):
    return response


# @app.route('/')
# def app_webapp_index():
#     return static_file(webapp_index)

'''
@app.route('/tv/<int:id>', defaults={'slug': None})
@app.route('/tv/<int:id>-<slug>')
def tv(id, slug):
    # ...
-----------
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def get_dir(path):
    return path
'''
'''
@app.errorhandler(404)
def notfound():
    """Serve 404 template."""
    return make_response(render_template("404.html"), 404)
'''
@app.route('/')
def app_webapp_index():
    return static_file(webapp_index)
    # return redirect(url_for(static_file(webapp_index)))

def static_file(filename):
    return send_from_directory(webapp_path, filename)


@app.route('/<path:filename>')
def app_webapp(filename):
    try:

        if re.match(r'\/?[^.]+\..*$', filename) is None:
            filename += '.html'
        return static_file(filename)
    except:
        filename = webapp_index
        return static_file(filename)



create_tables()

'''
    key = Column(Integer, primary_key=True, autoincrement=True)
    inserted = Column(DateTime, default=datetime.datetime.now())
    ## 실제 파일 저장.
    file_path = Column(String(300), nullable=True)
    ## 모델에 맞춰 파일명 저장.
    save_path = Column(String(300), nullable=True)
    ## 마크베이스 저장된 테이블 HYGAS.NAJU_C_HOUSE.30001.1
    machbase_name = Column(String(100), nullable=True)
    ## todo: 검침/예측, 인수, 지역
    purpose = Column(String(100), nullable=True)
    # resource = Column(String(100), nullable=True)
    resource = Column(Integer, ForeignKey('resource.key'))
    location = Column(Integer, ForeignKey('location.key'))
    ## 해당 파일의 시작-끝 기간.
    period = Column(String(100), nullable=True)
'''

@app.route('/datas/insert-records', methods=['GET'])
def app_data_insert():

    db_session.add_all([

        # DataTable(file_path=,save_path=,machbase_name=,purpose=,resource=,location=,period=)


    ])