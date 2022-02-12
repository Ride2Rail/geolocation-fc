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
    # if there was not anything written to cache
    if data is None:
        return "{'Cache reading error'}", 500
    elif not data:
        logger.info("No location data was extracted from cache")
        return "No location data", 200
    logger.info(f"Extracted the following data from chace: {data}")
    cache_writing = gm.write_cache_data(request_id, data)
    if cache_writing:
        return "OK", 200
    else:
        return "{'Cache writing error'}", 500

if __name__ == '__main__':
    os.environ["FLASK_ENV"] = "development"
    app.run(port=5123, debug=True, use_reloader=False)
    exit(0)