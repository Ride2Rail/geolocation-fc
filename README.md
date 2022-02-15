# geolocation-fc
Repository for geolocation encodings using the Nominatim service.
The API takes the coordinates stored in list _geo_attribute_list_ of class
_GeolcoationManager_ and extracts it from Offer Cache. 
Then are the coordinates transfered to city names using Nominatim api.
Next, all the coordinates are writen to Offer Cache under request with key under the key _request_id:city_coordinates:longitude:latitude_,
e.g., "9d1cfc79-90e5-446b-8fbc-5e0c5ea9efa7:city_coordinates:38.750229:-9.174333"
 with as the city as the value.

## Request example
To translate the coordinates, run the request with request_id behind the port as:
```bash
curl -v -X GET "http://127.0.0.1:5015/9d1cfc79-90e5-446b-8fbc-5e0c5ea9efa7"
```
If everything went fine, you shoud receive "OK", 200 response.