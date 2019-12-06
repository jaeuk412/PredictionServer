#-*- coding:utf-8 -*-

'''general'''
import datetime
'''library'''

'''directory'''
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
''' '''

Base = declarative_base()

class Login(Base):
    __tablename__ = 'login'
    key = Column(Integer, primary_key=True, autoincrement=True)
    inserted = Column(DateTime, default=datetime.datetime.now())
    id = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    level = Column(Integer, default=1)


class ResultTable(Base):
    __tablename__ = 'result_save'
    ## 고유 식별
    key = Column(Integer, primary_key=True, autoincrement=True)
    ## finished-inserted로 test 시간 측정.
    inserted = Column(DateTime, default=datetime.datetime.now())
    finished = Column(DateTime, nullable=True)
    ## 인수/검침, 나주/../광주, 시작날짜, 옵션(0,1), 모델이름, 저장경로2.
    resource = Column(String(100), nullable=False)
    location = Column(String(30), nullable=False)
    start_date = Column(Integer, nullable=True)
    temp_option = Column(Integer, nullable=True)
    sub_option = Column(Integer, nullable=True)
    model_name = Column(String(100), nullable=False)
    save_file1 = Column(String(300), nullable=True)
    save_file2 = Column(String(300), nullable=True)

    user_key = Column(Integer, nullable=True)

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
    resource = Column(String(100), nullable=True)
    location = Column(Integer, ForeignKey('location.key'))
    ## 해당 파일의 시작-끝 기간.
    period = Column(String(100), nullable=True)

class LocationTable(Base):
    __tablename__ = 'location'
    key = Column(Integer, primary_key=True, autoincrement=True)
    inserted = Column(DateTime, default=datetime.datetime.now())
    id = Column(String(50), unique=True, nullable=False)
    name = Column(String(50), nullable=True)
    name_en = Column(String(50), nullable=True)



# class DailyTable(Base):
#     __tablename__ = 'daily'
#     pkey = Column(Integer, primary_key=True, autoincrement=True)
#     inserted = Column(DateTime, default=datetime.datetime.now())
#     resource = Column(String(30), nullable=False)
#     location = Column(String(30), nullable=False)
#     start_date = Column(Integer, nullable=True)
#     # end_date = Column(Integer, nullable=True)
#     model_name = Column(String(50), nullable=False)
#     save_daily = Column(String(100), nullable=True)
#

# class MonthlyTable1(Base):
#     __tablename__ = 'monthly1'
#     pkey = Column(Integer, primary_key=True, autoincrement=True)
#     inserted = Column(DateTime, default=datetime.datetime.now())
#     resource = Column(String(30), nullable=False)
#     location = Column(String(100), nullable=False)
#     start_date = Column(Integer, nullable=True)
#     # end_date = Column(Integer, nullable=True)
#     model_name = Column(String(50), nullable=False)
#     temp_option = Column(Integer, nullable=False)
#     sub_option = Column(Integer, nullable=False)
#     save_daily = Column(String(100), nullable=True)
#     save_monthly = Column(String(100), nullable=True)
#
#
# class MonthlyTable2(Base):
#     __tablename__ = 'monthly2'
#     pkey = Column(Integer, primary_key=True, autoincrement=True)
#     inserted = Column(DateTime, default=datetime.datetime.now())
#     resource = Column(String(30), nullable=False)
#     location = Column(String(100), nullable=False)
#     start_date = Column(Integer, nullable=True)
#     # end_date = Column(Integer, nullable=True)
#     model_name = Column(String(50), nullable=False)
#     save_daily = Column(String(100), nullable=True)
#     save_monthly = Column(String(100), nullable=True)
#
# class YearlyTable(Base):
#     __tablename__ = 'yearly'
#     pkey = Column(Integer, primary_key=True, autoincrement=True)
#     inserted = Column(DateTime, default=datetime.datetime.now())
#     resource = Column(String(30), nullable=False)
#     location = Column(String(100), nullable=False)
#     start_date = Column(Integer, nullable=True)
#     # end_date = Column(Integer, nullable=True)
#     model_name = Column(String(50), nullable=False)
#     save_monthly = Column(String(200), nullable=True)
#     save_yearly = Column(String(200), nullable=True)
#     # year_range = Column(Integer, nullable=False)

# class Testjeju(Base):
#     __tablename__ = 'weather_jeju'
#     pkey = Column(Integer, primary_key=True, autoincrement=True)


# class DongEup(Base):
#     __tablename__ = 'dong_eup'
#     gong

