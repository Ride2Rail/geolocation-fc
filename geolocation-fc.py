import os
from flask import Flask, request
from r2r_offer_utils.advanced_logger import *

from codes.geolocators import GeoLocationManager

service_name = os.path.splitext(os.path.basename(__file__))[0]

logger = logging.getLogger(service_name)
config = ConfigLoader(LoggerFormatter(logger), service_name).config

app = Flask(service_name)

gm = GeoLocationManager(config)

# curl -X POST http://127.0.0.1:5015/compute -d '{"request_id": "9d1cfc79-90e5-446b-8fbc-5e0c5ea9efa7", "geo_attributes" = ["start_point", "end_point", "via_locations"]}' -H "Content-Type: application/json"
@app.route('/compute', methods=['POST'])
def extract():
    req_data = request.get_json()
    try:
        request_id = req_data['request_id']
        # ["start_point", "end_point", "via_locations"]
        geo_attribute_list = req_data['geo_attributes']
    except KeyError as ke:
        logger.error(f"Missing data in the request: {ke}")
        return "{'Wrong input data'}", 400

    data = gm.extract_cache_data(request_id, geo_attribute_list)
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