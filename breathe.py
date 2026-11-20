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

logging.info('Fetching data : ListSensors')
response = session.get(urlroot + "ListSensors", headers=headers)

response.raise_for_status()

#print ( response.content )

logging.info('Printing SiteCode')
data = response.json()

#print ( json.dumps( data , indent = 2 ) )

logging.info('Creating staging table...')

# Example to create a simple test table
StagingTable = db.Table('breathe_staging', dbmeta,
    db.Column('SiteCode', db.String(255)),
    db.Column('SiteName', db.String(255)),
    db.Column('DeviceCode', db.String(255)),
    db.Column('InstallationCode', db.String(255)),
    db.Column('Facility', db.String(255)),
    db.Column('Latitude', db.Float),
    db.Column('Longitude', db.Float),
    db.Column('Borough', db.String(255)),
    db.Column('SiteClassification', db.String(255)),
    db.Column('SensorHeightAboveGround', db.Float),
    db.Column('DistanceToKerb', db.Float),
    db.Column('SponsorName', db.String(255)),
    db.Column('SiteLocationType', db.String(255)),
    db.Column('StartDate', db.DateTime),
    db.Column('EndDate', db.DateTime),
    db.Column('PowerTag', db.String(255)),
    db.Column('SiteDescription', db.Text),
    db.Column('SitePhotoURL', db.String(255)),
    db.Column('SensorContract', db.String(255))
    )
dbmeta.create_all(engine)

logging.info("Loading data to staging table...")

for sensor in data:
    logging.info("Adding data for: " + sensor['SiteCode'])
#    print("SiteCode: " + sensor['SiteCode'])

    try:
        mystartdate = datetime.strptime(sensor['StartDate'],'%Y-%m-%dT%H:%M:%SZ')
    except:
        mystartdate = None

    try:
        myenddate = datetime.strptime(sensor['EndDate'],'%Y-%m-%dT%H:%M:%SZ')
    except:
        myenddate = None

    stmt = db.insert(StagingTable).values( SiteCode = sensor['SiteCode'],
        SiteName = sensor['SiteName'],
        DeviceCode = sensor['DeviceCode'],
        InstallationCode = sensor['InstallationCode'],
        Facility = sensor['Facility'],
        Latitude = sensor['Latitude'],
        Longitude = sensor['Longitude'],
        Borough = sensor['Borough'],
        SiteClassification = sensor['SiteClassification'],
        SensorHeightAboveGround = sensor['SensorHeightAboveGround'],
        DistanceToKerb = sensor['DistanceToKerb'],
        SponsorName = sensor['SponsorName'],
        SiteLocationType = sensor['SiteLocationType'],
        StartDate = mystartdate,
        EndDate = myenddate, 
        PowerTag = sensor['PowerTag'],
        SiteDescription = sensor['SiteDescription'],
        SitePhotoURL = sensor['SitePhotoURL'],
        SensorContract = sensor['SensorContract']
        )

    res = dbconn.execute(stmt) 
    dbconn.commit()

logging.info('Done.')
