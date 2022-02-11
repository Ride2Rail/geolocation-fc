import os
from flask import Flask, abort
from r2r_offer_utils.advanced_logger import *

from geolocators import GeoLocationManager

service_name = os.path.splitext(os.path.basename(__file__))[0]

logger = logging.getLogger(service_name)
config = ConfigLoader(LoggerFormatter(logger), service_name).config

app = Flask(service_name)

gm = GeoLocationManager(config)

@app.route('/<request_id>', methods=['GET'])
def get_data(request_id):
    data = gm.extract_cache_data(request_id)
    logger.info(f"extracted the following data: {data}")
    gm.write_cache_data(request_id, data)
    return "ok", 200

if __name__ == '__main__':
    os.environ["FLASK_ENV"] = "development"
    app.run(port=5123, debug=True, use_reloader=False)
    exit(0)