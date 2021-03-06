#-*- coding:utf-8 -*-

'''general'''
import datetime
'''library'''

'''directory'''
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
''' '''

Base = declarative_base()

class Login(Base):
    __tablename__ = 'login'
    key = Column(Integer, primary_key=True, autoincrement=True)
    # inserted = Column(DateTime, default=datetime.datetime.now())
    inserted = Column(DateTime(timezone=True), default=func.now())
    id = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    level = Column(Integer, default=1)


class ResultTable(Base):
    __tablename__ = 'result_save'
    ## 고유 식별
    key = Column(Integer, primary_key=True, autoincrement=True)
    ## finished-inserted로 test 시간 측정.
    inserted = Column(DateTime, nullable=True)
    finished = Column(DateTime, nullable=True)
    ## 인수/검침, 나주/../광주, 시작날짜, 옵션(0,1), 모델이름, 저장경로2.
    # resource = Column(String(100), nullable=False)
    resource = Column(Integer, ForeignKey('resource.key'))
    # location = Column(String(30), nullable=False)
    location = Column(Integer, ForeignKey('location.key'))
    start_date = Column(Integer, nullable=True)
    temp_option = Column(Integer, nullable=True)
    sub_option = Column(Integer, nullable=True)
    # model_name = Column(String(100), nullable=False)
    model = Column(Integer, ForeignKey('model.key'))
    save_file1 = Column(String(300), nullable=True)
    save_file2 = Column(String(300), nullable=True)
    user_key = Column(Integer, nullable=True)
    name = Column(String(100), nullable=True)
    descript = Column(String(100), nullable=True)

## 저장만 따로 마크베이스로. 실파일저장위치(파일명:najuaaaa)(DataSet/uploadfiles), 모델돌리려는 파일저장위치(파일명:naju_insu_2015)(prediction/data) 연결
class DataTable(Base):
    __tablename__ = 'data'
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
    file_name = Column(String(300))

class LocationTable(Base):
    __tablename__ = 'location'
    key = Column(Integer, primary_key=True, autoincrement=True)
    inserted = Column(DateTime, default=datetime.datetime.now())
    id = Column(String(50), unique=True, nullable=False)
    name = Column(String(50), nullable=True)
    name_en = Column(String(50), nullable=True)

class ResourceTable(Base):
    __tablename__ = 'resource'
    key = Column(Integer, primary_key=True, autoincrement=True)
    inserted = Column(DateTime, default=datetime.datetime.now())
    id = Column(String(100), unique=True, nullable=False)
    name = Column(String(50), nullable=True)
    explain = Column(String(500), nullable=True)

class ModelTable(Base):
    __tablename__ = 'model'
    key = Column(Integer, primary_key=True, autoincrement=True)
    inserted = Column(DateTime, default=datetime.datetime.now())
    id = Column(String(100), unique=True, nullable=False)
    name = Column(String(500), nullable=True)

class SmartcityTable(Base):
    __tablename__ = 'smartcity'
    key = Column(Integer, primary_key=True, autoincrement=True)
    inserted = Column(DateTime, default=datetime.datetime.now())
    icon = Column(String(100), nullable=True)
    title = Column(String(500), nullable=True)
    path = Column(String(500), unique=True, nullable=True)

