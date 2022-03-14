# Feature collector "Geolocation-fc"
***Version:*** 1.0

***Date:*** 15.02.2022

***Authors:***  [Milan Straka](https://github.com/bioticek), [Ľuboš Buzna](https://github.com/lubos31262); 
***Address:*** University of Žilina, Univerzitná 8215/1, 010 26 Žilina, Slovakia

# Description 

Feature collector extracts records from the Offer-cache containing geographical coordinates and translates
them using the Nominatim service into city names. Only records required by the Thor ranker are translated.
The city names are then written back to the Offer-cache.


The post request is calling the method ***compute*** from the ***"geolocation-fc.py"***.  The API takes the coordinates
stored in list _geo_attribute_list_ of class _GeolocationManager_ and extracts them from the Offer-Cache. 
The coordinates are rounded to 3 decimal spaces.  The rounded coordinates are translated to city names using Nominatim api.
All the coordinates (not rounded) are writen to the Offer-Cache under the key formated as _request_id:city_coordinates:longitude:latitude_.
with the city name as the value. 
The classes implementing the feature collector are stored in scripts ***"communicators.py"*** and ***"geolocators.py"***
in the folder [codes](https://github.com/Ride2Rail/geolocation-fc/tree/main/codes).


# Configuration
The following values of parameters can be defined in the configuration file ***"geolocation-fc.conf"***.

Section ***"running"***:
- ***"verbose"*** - if value __"1"__ is used, then feature collector is run in the verbose mode


Section ***"cache"***: 
- ***"host"*** - host address where the Offer-cache service is available
- ***"port"*** - port number where the Offer-cache service  is available


Section ***"running"***:
- ***"domain"*** - Domain of the Nominatim service. If value __"default"__ is used, then the public Nominatim service is used.
- ***"user"*** - User_agent to be sent to the public Nominatim service. If value __"default"__ is used, then the *user_agent* is randomly generated 
for each request. This can help improve the response as the public Nomination service limits the number of responses per
user_agent.

# Usage  
The API listens at "/compute" URL path and the port configured in the config file. 
The request should have the following parameters in the data part:
- ***"request_id"*** - request identifier
- ***"geo_attributes"*** - list of attribute names to be translated

An example of the POST request:
```bash
curl -X POST http://127.0.0.1:5015/compute -d '{"request_id": "123x", "geo_attributes": ["start_point", "end_point", "via_locations"]}' \
     -H "Content-Type: application/json"
```

## Responses
 - If everything went fine, the response code _200_ is returned.
 - In case of bad input data the response code _400_ is returned.
 - If the writing to the Offer-cache fails, the response code _500_ is returned.
