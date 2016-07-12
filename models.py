import os
import sys

from sqlalchemy import Column, Integer, String, Float, Date, UniqueConstraint, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc

from config import Config

config = Config()
db_connector = 'mysql://%s:%s@%s/%s' % (config.DB_USER, config.DB_PSW,config.HOST_URL,config.DB_NAME)
engine = create_engine(db_connector)

# create a configured "Session" class
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()
 
class GaData(Base):
    __tablename__ = config.DB_GA_TABLE
    id = Column(Integer, primary_key=True)
    ga_id = Column(String(250), nullable=False)
    client_name = Column(String(250), nullable=False)
    date = Column(Date, nullable=False)
    medium = Column(String(250), nullable=False)
    sessions = Column(Integer, nullable=False)
    transactions = Column(Integer, nullable=False)
    revenue = Column(Float, nullable=False)
    goalCompletions1 = Column(Integer, nullable=False)

    __table_args__ = (UniqueConstraint('ga_id', 'client_name', 'date','medium', name='_client_month_uc'),)

    @staticmethod
    def update(row):
        session.query(GaData).\
            filter(and_(GaData.ga_id == row['ga_id'],
                        GaData.client_name == row['client_name'],
                        GaData.date == row['date'],
                        GaData.medium == row['medium'])
                    ).update(row)
        session.commit()

class ForecastData(Base):
    __tablename__ = config.DB_FORECAST_TABLE
    id = Column(Integer, primary_key=True)
    ga_id = Column(String(250), nullable=False)
    client_name = Column(String(250), nullable=False)
    fcast_start_date = Column(Date, nullable=False)
    date = Column(Date, nullable=False)
    medium = Column(String(250), nullable=False)
    mean = Column(Integer, nullable=False)
    lower_85 = Column(Integer, nullable=False)
    upper_85 = Column(Integer, nullable=False)
    lower_95 = Column(Integer, nullable=False)
    upper_95 = Column(Integer, nullable=False)
    accuracy_mape = Column(Float)

    __table_args__ = (UniqueConstraint('ga_id', 'client_name','fcast_start_date', 'date','medium', name='_client_month_uc'),)

    @staticmethod
    def update(row):
        session.query(ForecastData).\
            filter(and_(ForecastData.ga_id == row['ga_id'],
                        ForecastData.client_name == row['client_name'],
                        ForecastData.date == row['date'],
                        ForecastData.medium == row['medium'],
                        ForecastData.fcast_start_date == row['fcast_start_date'])
                    ).update(row)
        session.commit()

def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        session.query(model).filter_by(**kwargs).update(defaults, False)
        return instance, True
        
    else:
        params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
        params.update(defaults or {})
        instance = model(**params)
        session.add(instance)


Base.metadata.create_all(engine)