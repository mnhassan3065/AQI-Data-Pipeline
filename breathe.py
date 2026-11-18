#!/usr/bin/python3

import logging
import requests

import sqlalchemy as db
from datetime import datetime

from config import get_config

logger = logging.getLogger(__name__)

logging.basicConfig(filename='breathe.log', level=logging.INFO)
logger.info('Started')

logging.info('Reading configuration from environment / .env...')
cfg = get_config()

# Log only the non-secret part of the connection details.
logging.info("DB target: " + cfg.safe_summary())
logging.info("Attempting to connect to db...")

engine = db.create_engine(cfg.database_url())

dbconn = engine.connect()
dbmeta = db.MetaData()

# Example to create a simple test table
#ExampleTable = db.Table('example', dbmeta,
#    db.Column('id', db.Integer, primary_key=True),
#    db.Column('name', db.String(20), nullable=False)
#    )
#dbmeta.create_all(engine)

headers = {'X-API-KEY': cfg.breathe_api_key}

logging.info('Setting up request session.')
session = requests.Session()
session.headers.update(headers)

logging.info('Fetching data : ListSensors')
response = session.get(cfg.breathe_url_root + "ListSensors", timeout=30)

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
