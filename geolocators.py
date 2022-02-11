import logging
from time import sleep
from random import randint

import geojson
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from communicators import OfferCacheCommunicator

logger = logging.getLogger('data_provider_api.DataExtractors')


class GeoLocationManager:
    def __init__(self, config):
        self.occ = OfferCacheCommunicator(config)
        self.geo_attribute_list = ["start_point", "end_point", "via_locations"]
        self.geo_datatype_list = ["v", "v", "v"]

    def extract_cache_data(self, request_id) -> dict:
        """
        Extracts the data in attribute_list, as well as leg information obtained by extractDetailedData
        :param request_id:
        :return: dictionary with keys from attribute list, and information with key as leg_information
        """
        res = {}
        # create geolocation extractor
        ge = GeoLocationExtractor()
        try:
            res = self.occ.redis_request_level_item(request_id, self.geo_attribute_list, self.geo_datatype_list)
            # extract location data here
            res = self.extrac_coord_list(res, ge)
        except KeyError as ke:
            logger.error(f"OCCommunicationManager error, key not found in received data from offer cache: {ke}")

        return res

    def write_cache_data(self, request_id, coord_city_dict):
        """
        writes the data to the cache
        :param request_id:
        :param coord_city_dict: dictionary with coordinate tuples as keys and citynames as values
        :return: if the writing was successful
        """
        self.occ.write_coords(request_id, coord_city_dict)

    def extrac_coord_list(self, oc_dict, geo_loc_extractor):
        extracted_keys = [] # list of keys that were extracted
        geo_coord_list = [] # list of geocoordinates
        for key in self.geo_attribute_list:
            if key in oc_dict:
                try:
                    # extract coordinates and puts them into a list
                    coord_list = self.extract_coords_geojson(oc_dict, key)
                    # if it is a list append it to a list
                    if type(coord_list) is list:
                        geo_coord_list += coord_list
                    else:
                        geo_coord_list.append(coord_list)
                    extracted_keys.append(key)
                except Exception as ex:
                    logger.error(f"Error when extracting locations in OCCommunicationManager: {ex}")
                    oc_dict = None
        if len(geo_coord_list) > 0:
            res_list = geo_loc_extractor.process_location_list(geo_coord_list)
            return res_list
        return []

    def extract_coords_geojson(self, oc_data, key):
        try:
            coord_list = geojson.loads(oc_data[key])['coordinates']
            float_coords = []
            # if it is a list of coords
            if type(coord_list[0]) is list:
                for coords in coord_list:
                    coords = self.float_coords(coords)
                    if coords is not None:
                        float_coords.append(coords)
            else:
                float_coords = self.float_coords(coord_list)
            return float_coords
        except Exception as ex:
            logger.error(f"Error when extracting locations in OCCommunicationManager: {ex}")
        return None

    @staticmethod
    def float_coords(coords):
        try:
            return float(coords[1]), float(coords[0])
        except ValueError as ve:
            logger.error(f'Error when converting coordinates from string to float: {ve}')
        return None


class GeoLocationExtractor:

    def __init__(self):
        user_agent = 'user_r_{}'.format(randint(1000, 9999))
        self.geolocator = Nominatim(user_agent=user_agent)

    def reverse_geocode(self, lat, lon, sleep_millis=1200):
        """
        Extract location data from the Nominatim service. In case the server gets full,
        source of inspiration: https://stackoverflow.com/questions/60083187/python-geopy-nominatim-too-many-requests
        :param lat: latitude
        :param lon: longitude
        :param sleep_millis: Max. miliseconds to sleep in case of
        :return:
        """
        try:
            return self.geolocator.reverse(str(lat) + "," + str(lon))
        except GeocoderTimedOut:
            logging.info('TIMED OUT: GeocoderTimedOut: Retrying...')
            sleep(randint(1 * 100, round(sleep_millis / 10)) / 100)
            return self.reverse_geocode(lat, lon, sleep_millis)
        except GeocoderServiceError as e:
            logging.info('CONNECTION REFUSED: GeocoderServiceError encountered.')
            logging.error(e)
            return None
        except Exception as e:
            logging.error(f"Unexpected exception at GeoLocator {e}")

    def coordinates_to_city(self, lat, lon):
        """
        Uses reverse_geocode function to extract data from Nominatim and then extracts the city
        :param lat: latitude
        :param lon: longitude
        :return: city (str) corresponding to the coordinates
        """
        location = self.reverse_geocode(lat, lon)
        city = None
        if location is not None and 'address' in location.raw:
            city = location.raw['address'].get('city', location.raw['address'].get('town'))
            if city is None:
                logger.error("Missing city in location dictionary in GeoLocationExtractor")
        else:
            logger.error("Location address not obtained in GeoLocationExtractor")
        logger.info(f'successfully obtained city {city} for the location: {lat}, {lon}')
        return city

    def city_obtainer(self, loc_dict, round_dec=3):
        """
        For each location in the loc_dict extract the city using the method get_city_location. The coordinates are
        first rounded to round_dec decimal points. Then only for the unique coordinates are cities extracted.
        The mapping of the original coordinates to the rounded coordinates is kept in coordinate_mapper dictionary.
        After extraction, the cities are mapped back to the original coordinates.
        :param loc_dict: dictionary storing location with lat, lon as  tuples
        :param round_dec: number of decimals to which round the coordinates, to decrease the number of requests
        :return: loc_dict with original coordinates as keys and city names as values
        """
        simplified_location_mapper = {}
        # simplify the coordinates and map the original to a dictionary
        for coords in loc_dict.keys():
            try:
                # round the coordinates to avoid sending duplicities
                round_coords = (round(coords[0], round_dec), round(coords[1], round_dec))
                # creates or appends to the list with the given coordinates
                if round_coords in simplified_location_mapper:
                    simplified_location_mapper[round_coords].append(coords)
                else:  # the key is new so also add it to the city dict
                    simplified_location_mapper[round_coords] = [coords]
            except TypeError as te:
                logger.error(f"Error in type: {te}")

        # extract the cities and map them back to coordinates
        for round_coords in simplified_location_mapper.keys():
            # extract the city
            city = self.coordinates_to_city(round_coords[0], round_coords[1])
            # map it back to the coordinates
            for coords in simplified_location_mapper[round_coords]:
                loc_dict[coords] = city
        return loc_dict

    def __reshape_locations(self, locations):
        loc_dict = {}
        for loc in locations:
            loc_dict[(loc[0], loc[1])] = None
        return loc_dict

    def process_location_list(self, coord_list):
        # reshape the list of locations
        loc_dict = self.__reshape_locations(coord_list)
        # obtain the cities
        # simplified_locs = self.loc_list_simplifier(loc_dict, 3)
        simplified_locs = self.city_obtainer(loc_dict, 3)
        return simplified_locs

    # source: http://www.martinbroadhurst.com/removing-duplicates-from-a-list-while-preserving-order-in-python.html
    def unique(self, sequence):
        seen = set()
        return [x for x in sequence if not (x in seen or seen.add(x))]
