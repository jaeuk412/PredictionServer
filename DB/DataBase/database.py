#-*- coding:utf-8 -*-
import os

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker, joinedload

from flask import jsonify


from DB.DataBase.models import Base

# DEBUG = True

# 다른 디비 connect 및 쿼리.
def connect(user, password, db, host, port):
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)

    engine = create_engine(url, pool_size=800, max_overflow=800, client_encoding='utf8')

    # meta = sqlalchemy.MetaData(bind=con, reflect=True)

    return engine  # , meta
# port: postgres, ?, PredictionServe, '0.0.0.0' ,25005
dbsearch = connect('postgres','0000','PredictionServer','0.0.0.0','5432')

dbsearch1 = connect('postgres','sp597886', 'smart-city', '220.90.81.106', '19415')

#-------------------------------------------------------------

basedir = os.path.abspath(os.path.dirname(__file__))

# engine = create_engine(postgresql+psycopg2://username:password@host/database)
engine = create_engine('postgresql+psycopg2://postgres:0000@localhost/PredictionServer',pool_size=800, max_overflow=800)

metadata = MetaData()
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

def create_tables():
    Base.metadata.create_all(bind=engine)


