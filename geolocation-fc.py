import os
from flask import Flask, abort
from r2r_offer_utils.advanced_logger import *

service_name = os.path.splitext(os.path.basename(__file__))[0]

logger = logging.getLogger(service_name)
config = ConfigLoader(LoggerFormatter(logger), service_name).config

app = Flask(service_name)

@app.route('/<request_id>', methods=['GET'])
def write_data(request_id):
    return "", 200