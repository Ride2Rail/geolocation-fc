# Feature collector "Geolocation-fc"
***Version:*** 1.0

***Date:*** 15.02.2022

***Authors:***  [Milan Straka](https://github.com/bioticek), [Ľuboš Buzna](https://github.com/lubos31262); 
***Address:*** University of Žilina, Univerzitná 8215/1, 010 26 Žilina, Slovakia

# Description 

Repository for encoding geolocations to city names using the Nominatim service. 
It extracts the coordinates stored in data provided in the request and translates
them using the Nominatim service into city names. The city names are then written to cache.

When the post request is received, the method ***compute*** from the ***"geolocation-fc.py"*** is called.
The API takes the coordinates stored in list _geo_attribute_list_ of class
_GeolocationManager_ and extracts them from Offer Cache. 
To prevent overloading of the Nominatim service the coordinates are first rounded to 3 decimal spaces. 
Next the rounded coordinates are transferred to city names using Nominatim api.
Lastly, all the coordinates (not rounded) are writen to Offer Cache under a key with format _request_id:city_coordinates:longitude:latitude_,
e.g., "9d1cfc79-90e5-446b-8fbc-5e0c5ea9efa7:city_coordinates:38.750229:-9.174333",
 with the city name as the value. 
The classes in which the most of this api is implemented are stored in scripts ***"communicators.py"*** and ***"geolocators.py"***
in the folder [codes](https://github.com/Ride2Rail/geolocation-fc/tree/main/codes).

# Configuration

The following values of parameters can be defined in the configuration file ***"geolocation-fc.conf"***.

Section ***"running"***:
- ***"verbose"*** - if value __"1"__ is used, then feature collector is run in the verbose mode,

Section ***"cache"***: 
- ***"host"*** - host address where the cache service that should be accessed by ***"geolocation-fc"*** is available
- ***"port"*** - port number where the cache service that should be accessed used by ***"geolocation-fc"*** is available

Section ***"running"***:
- ***"domain"*** - Domain name for the Nominatim service. If value __"default"__ is used, then the default online Nominatim service is used.
- ***"user"*** - User for the Nominatim service. If value __"default"__ is used, then a random username is generated for each request.

# Usage  

The API listens at "/compute" URL path and the port configured in the config file. 
It requires the following parmeters in the data part:
- ***"request_id"*** - request identifier
- ***"geo_attributes"*** - list of geo attributes for which the translation will be provided

An example of the POST request:
```bash
curl -X POST http://127.0.0.1:5015/compute -d '{"request_id": "123x", "geo_attributes": ["start_point", "end_point", "via_locations"]}' \
     -H "Content-Type: application/json"
```

## Responses
 - If everything went fine, you should receive _"OK", 200_ response.
 - In case of bad input data you receive _400_ response code.
 - If the writing to cache fails, you receive _500_ response code.
