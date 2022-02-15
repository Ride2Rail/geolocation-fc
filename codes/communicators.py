import redis
import logging
import itertools

logger = logging.getLogger('geolocation-fc.OfferCacheCommunication')


class OfferCacheCommunicator:
    """
        Establishes connection with the offer cache. Provides methods to communicate with offer cache.
    """

    def __init__(self, config, data=None):
        # get the ports
        # self.data = data
        if config is not None:
            # read connection parameters from the config file
            CACHE_HOST = config.get('cache', 'host')
            CACHE_PORT = config.get('cache', 'port')
            logger.info(f"Connecting to offer cache: CACHE_HOST = {CACHE_HOST}, CACHE_PORT = {CACHE_PORT}")
            try:
                # establish connection to the offer cache
                self.cache = redis.Redis(host=CACHE_HOST, port=CACHE_PORT, decode_responses=True)
            except redis.exceptions.ConnectionError as exc:
                logger.error("Connection to the offer cache has not been established.")
        else:
            logger.error('Could not read config file in offer_cache_extractor.py')

    def write_coords(self, request_id, coord_dict):
        pipe = self.cache.pipeline()
        for coord, city in coord_dict.items():
            if city is not None:
                pipe.set(f'{request_id}:city_coordinates:{coord[0]}:{coord[1]}', city)
        try:
            pipe_res_list = pipe.execute()
        # Raised if incorrect key types were provided
        except redis.exceptions.RedisError as re:
            logger.error(f"Error when reading from cache, probably wrong data type: \n{re}")
            return False
        return True

    def redis_request_level_item(self, request_id, request_level_keys, request_level_types):
        """
        Obtains the keys provided in request_level_keys from OfferCache, with types specified in request level types.
        In case a wrong type of any key is provided, None is returned.
        :param request_id: id of the request
        :param request_level_keys: keys on the request level
        :param request_level_types: types of the keys on the request level
        :return: dictionary with a dictionary for each key
        """
        # dictionary of possible values
        transl_dict = {"l": "list", "v": "value"}
        pipe = self.cache.pipeline()
        index_list = [] # list of indexed which were not skipped
        res_dict = {} # dictionary for results
        # iterate over the keys
        for key, data_type, i in itertools.zip_longest(request_level_keys, request_level_types, range(0, len(request_level_keys))):
            # if the key type is a valid type add it to the pipe, otherwise set the corresponding key as none
            if data_type in transl_dict.keys():
                self.redis_universal_get(pipe, request_id, key, data_type)
                index_list.append(i)
            else:
                # removes the key. This can by replaced with res_dict[key] = None
                del res_dict[key]
        # execute the pipe
        try:
            pipe_res_list = pipe.execute()
        # Raised if incorrect key types were provided
        except redis.exceptions.RedisError as re:
            logger.error(f"Error when reading from cache, probably wrong data type: \n{re}")
            return {}
        # extract the data from the pipe to the dictionary, skips attributes with unexpected data type
        for pipe_req, i in itertools.zip_longest(pipe_res_list, index_list):
            if pipe_req is None or len(pipe_req) == 0:
                del res_dict[request_level_keys[i]]
            else:
                res_dict[request_level_keys[i]] = pipe_req

        return res_dict

    def redis_universal_get(self, pipe, request_id, key, type):
        """
        adds the request to the Redis pipe based on the type of the key
        :param pipe: pipe to push the data
        :param request_id: id of the request
        :param key: key for the Redis database
        :param type: data type of the key
        :return:
        """
        if type == 'l':
            pipe.lrange(f"{request_id}:{key}", 0, -1)
        if type == 'v':
            pipe.get(f"{request_id}:{key}")