# -*- coding: utf-8 -*-

# general
import datetime
import re

# library
from flask import Flask, send_from_directory

# directory
from DB.DataBase.database import create_tables
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

app.config['SESSION_TYPE'] = 'memcached'
app.config['SECRET_KEY'] = 'super secret key'
app.config['SESSION_COOKIE_AGE'] = 1500
app.config['MAX_CONTENT_LENGTH'] = 20000000
app.permanent_session_lifetime = datetime.timedelta(days=1)

# celery = make_celery(app)

create_tables()

# @celery.task()
# def add_together(a, b):
#     print(a+b)
#     return a + b
#
#
# result = add_together.delay(23, 42)
# result.wait()
# #################################################
# # Socket
#
# @socketio.on('connect')
# def connect():
#     emit("response",{'data':'datavalue'})

##################################################
# global headers for CORS

@app.after_request
## origin=ip_path는 해당 컴터
@crossdomain(origin='*', headers='content-type')
def app_global_headers(response):
    return response


##################################################
# routing static files
webapp_path = 'webapp'
webapp_index = 'index.html'


def static_file(filename):
    return send_from_directory(webapp_path, filename)


@app.route('/')
def app_webapp_index():
    return static_file(webapp_index)


@app.route('/<path:filename>')
def app_webapp(filename):
    if re.match(r'\/?[^.]+\..*$', filename) is None:
        filename += '.html'
    return static_file(filename)
