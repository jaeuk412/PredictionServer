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
    pkey = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String(100), unique=True, nullable=False)
    pw = Column(String(100), nullable=False)
    level = Column(Integer, default=1)
#
# class TestTable(Base):
#     __tablename__ = 'testtable'
#     pkey = Column(Integer, primary_key=True, autoincrement=True)
#     inserted = Column(DateTime, default=datetime.datetime.now())
#     name = Column(String(100), nullable=False)

class DailyTable(Base):
    __tablename__ = 'daily'
    pkey = Column(Integer, primary_key=True, autoincrement=True)
    inserted = Column(DateTime, default=datetime.datetime.now())
    target_sort = Column(String(30), nullable=False)
    target_area = Column(String(30), nullable=False)
    start_date = Column(Integer, nullable=False)
    model_name = Column(String(50), nullable=False)

class MonthlyTable1(Base):
    __tablename__ = 'monthly1'
    pkey = Column(Integer, primary_key=True, autoincrement=True)
    inserted = Column(DateTime, default=datetime.datetime.now())
    target_sort = Column(String(30), nullable=False)
    target_area = Column(String(100), nullable=False)
    start_date = Column(Integer, nullable=False)
    model_name = Column(String(50), nullable=False)
    month_range = Column(Integer, nullable=False)
    temp_option = Column(Integer, nullable=False)
    sub_option = Column(Integer, nullable=False)

class MonthlyTable2(Base):
    __tablename__ = 'monthly2'
    pkey = Column(Integer, primary_key=True, autoincrement=True)
    inserted = Column(DateTime, default=datetime.datetime.now())
    target_sort = Column(String(30), nullable=False)
    target_area = Column(String(100), nullable=False)
    start_date = Column(Integer, nullable=False)
    model_name = Column(String(50), nullable=False)
    month_range = Column(Integer, nullable=False)

class YearlyTable(Base):
    __tablename__ = 'yearly'
    pkey = Column(Integer, primary_key=True, autoincrement=True)
    inserted = Column(DateTime, default=datetime.datetime.now())
    target_sort = Column(String(30), nullable=False)
    target_area = Column(String(100), nullable=False)
    start_date = Column(Integer, nullable=False)
    model_name = Column(String(50), nullable=False)
    # year_range = Column(Integer, nullable=False)

# class Testjeju(Base):
#     __tablename__ = 'weather_jeju'
#     pkey = Column(Integer, primary_key=True, autoincrement=True)


# class DongEup(Base):
#     __tablename__ = 'dong_eup'
#     gong

