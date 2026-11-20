#!/usr/bin/python3

import logging
import configparser
import json
import requests

import sqlalchemy as db
from datetime import datetime

logger = logging.getLogger(__name__)

logging.basicConfig(filename='log/breathe.log', level=logging.INFO)
logger.info('Started')

Config = configparser.ConfigParser()

logging.info('Reading config file...')
Config.read("project.ini")

urlroot = Config.get('Breathe', 'URLROOT')
apikey = Config.get('Breathe', 'APIKEY')

mysqldbconnstring = Config.get('MYSQLDB', 'CONNSTR')

logging.info("DB Connstring: " + mysqldbconnstring) 
logging.info("Attempting to connect to db...")

engine = db.create_engine(mysqldbconnstring, echo=True)

dbconn = engine.connect()
dbmeta = db.MetaData()

headers = {'X-API-KEY': apikey}

logging.info('Setting up request session.')
session = requests.Session()
session.headers.update(headers)

logging.info('Fetching data : SensorData')
response = session.get(urlroot + "SensorData", headers=headers)

response.raise_for_status()

#print ( response.content )

data = response.json()

logging.info('Creating staging table...')

# Example to create a simple test table
StagingTable = db.Table('breathe_sensordata_staging', dbmeta,
    db.Column('Species', db.String(255)),
    db.Column('Source', db.String(255)),
    db.Column('Units', db.String(255)),
    db.Column('SiteCode', db.String(255)),
    db.Column('DateTime', db.DateTime),
    db.Column('Duration', db.String(255)),
    db.Column('ScaledValue', db.Float),
    db.Column('RatificationStatus', db.String(255)),
    db.Column('SensorContract', db.String(255))
    )
dbmeta.create_all(engine)

logging.info("Loading data to staging table...")

for sensor in data:
    logging.info("Adding data for: " + sensor['SiteCode'])
#    print("SiteCode: " + sensor['SiteCode'])

    try:
        mydatetime = datetime.strptime(sensor['DateTime'],'%Y-%m-%dT%H:%M:%SZ')
    except:
        mydatetime = None

    stmt = db.insert(StagingTable).values( Species = sensor['Species'],
        Source = sensor['Source'],
        Units = sensor['Units'],
        SiteCode = sensor['SiteCode'],
        DateTime = mydatetime,
        Duration = sensor['Duration'],
        ScaledValue = sensor['ScaledValue'] if sensor['ScaledValue'] else None,
        RatificationStatus = sensor['RatificationStatus'],
        SensorContract = sensor['SensorContract']
        )

    res = dbconn.execute(stmt) 
    dbconn.commit()

logging.info('Done.')
