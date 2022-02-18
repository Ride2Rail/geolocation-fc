import os
from flask import Flask, request
from r2r_offer_utils.advanced_logger import *

from codes.geolocators import GeoLocationManager

service_name = os.path.splitext(os.path.basename(__file__))[0]

logger = logging.getLogger(service_name)
config = ConfigLoader(LoggerFormatter(logger), service_name).config

app = Flask(service_name)

gm = GeoLocationManager(config)
# curl --header 'Content-Type: application/json' \
#        --request POST  \
#        --data '{"request_id": "9d1cfc79-90e5-446b-8fbc-5e0c5ea9efa7" }' \
#          http://localhost:5015/compute

# curl -v -X GET "http://127.0.0.1:5015/9d1cfc79-90e5-446b-8fbc-5e0c5ea9efa7"
@app.route('/compute', methods=['POST'])
def extract():
    req_data = request.get_json()
    request_id = req_data['request_id']
    data = gm.extract_cache_data(request_id)
    # if there was not anything written to cache
    if data is None:
        return "{'Cache reading error'}", 500
    elif not data:
        logger.info("No location data was extracted from cache")
        return "No location data", 200
    logger.info(f"Extracted the following data from cache: {data}")
    cache_writing = gm.write_cache_data(request_id, data)
    if cache_writing:
        return "OK", 200
    else:
        return "{'Cache writing error'}", 500

if __name__ == '__main__':
    os.environ["FLASK_ENV"] = "development"
    app.run(port=5015, debug=True, use_reloader=False)
    exit(0)