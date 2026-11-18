#!/usr/bin/python3

import logging

from flask import Flask, jsonify
import sqlalchemy as db

from config import get_config

app = Flask(__name__)

logger = logging.getLogger(__name__)
logging.basicConfig(filename='project-bottle.log', level=logging.INFO)

logging.info('Reading configuration from environment / .env...')
cfg = get_config()

# Log only the non-secret part of the connection details.
logging.info("DB target: " + cfg.safe_summary())
logging.info("Attempting to connect to db...")

engine = db.create_engine(cfg.database_url())

dbconn = engine.connect()
dbmeta = db.MetaData()
dbmeta.reflect(bind=engine)

@app.route('/hello')
def hello():
    return "Hello World!"

@app.route('/listsensors')
def listsensors():
    breathe_staging = dbmeta.tables['breathe_staging']
    qry = breathe_staging.select()
    results = dbconn.execute(qry).mappings().all()
    results_dict = [dict(r) for r in results]
#    for row in result:
#        print ( row ) 
    return jsonify(json_list = results_dict)

if __name__ == '__main__':
    logger.info('Started')
    app.run(host=cfg.flask_host, port=8080, debug=cfg.flask_debug)

