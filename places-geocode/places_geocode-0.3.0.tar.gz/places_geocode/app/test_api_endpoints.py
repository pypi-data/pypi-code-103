import requests
import time
import pymongo
import ssl
import json

from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from scipy.spatial import ConvexHull
from difflib import SequenceMatcher
from numba import njit
from CythonOperations import zip_coordinate, TFIDF_max, null_parameters


def test_endpoints():
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJtYXJ0aW4ubWFzaGFsb3YiLCJleHAiOjE2MjU5ODI1NjV9.OPugeH0picyrl9UrvWudv15S3tUBezZJQqOtdhSKuTY'
    my_headers = {'Authorization': token,
                  'runtime': 'X-Process-Time',
                  'accept': 'application/json'}
    url = 'http://127.0.0.1:8000/load_properties_api/parcel?latitude=43.0961466&longitude=-77.6337776&radius=100&username=martin.mashalov&reverse_param=false'
    start = time.perf_counter()
    data = requests.get(url,
                        headers=my_headers)

    print(data.json())
    print(time.perf_counter() - start)


def create_test_file_coordinates():
    client = pymongo.MongoClient(
        'mongodb+srv://martin_mashalov:Barca2004!@locationpoints.wi1dk.mongodb.net/test',
        ssl_cert_reqs=ssl.CERT_NONE)
    db = client['PeekDB']

    geoCoords = db['propLocations']
    json_structure = {'coordinates': []}

    with open('../analytics/sample_data/test_file_coordinates.json', 'a+') as file:
        for doc in geoCoords.find({})[0:20]:
            coordinates = doc['location']['coordinates']
            json_structure['coordinates'].append(coordinates)
        print(json_structure)
        json.dump(json_structure, file)


# create_test_file_coordinates()

def create_test_file_addresses():
    client = pymongo.MongoClient(
        'mongodb+srv://martin_mashalov:Barca2004!@locationpoints.wi1dk.mongodb.net/test',
        ssl_cert_reqs=ssl.CERT_NONE)
    db = client['PeekDB']

    geoCoords = db['propLocations']
    json_data = {'addresses': []}

    with open('test_file_addresses.json', 'a+') as file:
        for doc in geoCoords.find({})[0:20]:
            number = doc['properties']['number']
            street = doc['properties']['street']
            city = doc['properties']['city']
            postcode = doc['properties']['postcode']
            region = doc['properties']['region']
            unit = doc['properties']['unit']

            if unit != '':
                address = f'{number} {street}, {city}, {region}, {postcode}, {unit}'
            else:
                address = f'{number} {street}, {city}, {region}, {postcode}'

            json_data['addresses'].append(address)
        print(json_data)
        json.dump(json_data, file)


# create_test_file_addresses()

def create_test_spreadsheet():
    client = pymongo.MongoClient(
        'mongodb+srv://martin_mashalov:Barca2004!@locationpoints.wi1dk.mongodb.net/test',
        ssl_cert_reqs=ssl.CERT_NONE)
    db = client['PeekDB']

    geoCoords = db['propLocations']
    json_data = {'addresses': []}

    with open('../analytics/sample_data/test_spreadsheet_address.json', 'a+') as file:
        for doc in geoCoords.find({})[:100]:
            number = doc['properties']['number']
            street = doc['properties']['street']
            city = doc['properties']['city']
            postcode = doc['properties']['postcode']
            region = doc['properties']['region']
            unit = doc['properties']['unit']

            if unit != '':
                address = f'{number} {street}, {city}, {region}, {postcode}, {unit}'
            else:
                address = f'{number} {street}, {city}, {region}, {postcode}'

            json_data['addresses'].append(address)
        json.dump(json_data, file)


# create_test_spreadsheet()
def create_coordinates_spreadsheet():
    client = pymongo.MongoClient(
        'mongodb+srv://martin_mashalov:Barca2004!@locationpoints.wi1dk.mongodb.net/test',
        ssl_cert_reqs=ssl.CERT_NONE)
    db = client['PeekDB']

    geoCoords = db['propLocations']
    json_data = {'coordinates': []}

    with open('../analytics/sample_data/test_spreadsheet_coordinates.json', 'a+') as file:
        for doc in geoCoords.find({})[:14000]:
            coordinate = doc['location']['coordinates']

            json_data['coordinates'].append(coordinate)
        json.dump(json_data, file)


# create_coordinates_spreadsheet()

client = pymongo.MongoClient(
    'mongodb+srv://martin_mashalov:Barca2004!@locationpoints.wi1dk.mongodb.net/test',
    ssl_cert_reqs=ssl.CERT_NONE)
db = client['PeekDB']
geoCoords = db['propLocations']


def find_similarity(street, street_comparison) -> float:
    return SequenceMatcher(None, street.lower(), street_comparison['properties']['street'].lower()).ratio()


def polygon_search():
    # edges = [[[73.705034, 41.504346], [73.820142, 41.509602], [73.724686, 41.460176], [73.705034, 41.504346]]]
    edges = [[[41.010639, 73.860892], [41.010777, 73.862245], [41.011537, 73.862129], [41.010639, 73.860892]]]
    # new_edges = [[[41.010639, 73.860892], [41.010777, 73.862245], [41.011537, 73.862129]]]

    start = time.perf_counter()
    query = geoCoords.find({"location": {"$geoWithin": {"$geometry": {"type": "Polygon", "coordinates": edges}}}})
    print(query.count())
    print(time.perf_counter() - start)


# polygon_search()


def query():
    """test query function"""
    result = geoCoords.find(
        {'$and': [{'properties.number': str(20)}, {'properties.postcode': str(10522)}]})
    return result


def test_similarity():
    """test similarity func with TFIDF algorithm"""

    street_query = "Manor House"

    result = query()

    current_max = 0
    current_max_result = None

    for street_comparison in result:
        similarity = SequenceMatcher(None, street_query.lower(),
                                     street_comparison['properties']['street'].lower()).ratio()

        if similarity > current_max:
            current_max = similarity
            current_max_result = street_comparison
        else:
            continue

    return [current_max, current_max_result, current_max_result['properties']['street']]


"""start1 = time.perf_counter()
print(TFIDF_max.find_max_similarity("Manor House", query()))
print(time.perf_counter() - start1)

start2 = time.perf_counter()
print(test_similarity())
print(time.perf_counter() - start2)"""


def create_coordinate_test(lats: list, longs: list, reverse_param: bool):
    """
    :param lats:
    :param longs:
    :param reverse_param:
    """

    if reverse_param:
        return [[long, lat] for lat, long in zip(lats, longs)]
    else:
        return [[lat, long] for lat, long in zip(lats, longs)]


"""start = time.perf_counter()
create_coordinate_test([43.0900963, 43.0913689, 43.0920867], [-77.6463877, -77.6467333, -77.6439961], False)
first_time = time.perf_counter() - start

start2 = time.perf_counter()
zip_coordinate.coordinate_zipped([43.0900963, 43.0913689, 43.0920867, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], [-77.6463877, -77.6467333, -77.6439961, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3], False)
print(first_time/(time.perf_counter() - start2))"""


def boolean_test1():
    """
    return: boolean test
    """
    x = 5
    print(not not x == 5)


def boolean_test2():
    """
    return: boolean test
    """
    x = 5
    print(bool(x == 5))


"""not_array = []
bool_array = []

for _ in range(100000):
    start1 = time.perf_counter()
    boolean_test1()
    not_time = time.perf_counter() - start1
    not_array.append(not_time)

    start2 = time.perf_counter()
    boolean_test2()
    bool_time = time.perf_counter() - start2
    bool_array.append(bool_time)

print(sum(not_array), "----", sum(bool_array))
print(sum(not_array) <= sum(bool_array))"""


# noinspection PyCompatibility
def optimize_nulls(original: list, new: list):
    """replace null values in address list excluding the """

    optimized_original: list = [original[0]]

    for i in range(1, len(original)):
        if new[i] == '':
            optimized_original.append(original[i])
        else:
            optimized_original.append(new[i])

    return optimized_original


"""start1 = time.perf_counter()
print(optimize_nulls(
    ['Manor House Lane', 10522, 20, 'NY', '', 'Dobbs Ferry'],
    ['MANOR HOUSE LN', 10522, 20, '', '', 'Dobbs Ferry']
))
print(time.perf_counter() - start1)

start2 = time.perf_counter()
print(null_parameters.minimize_nulls(
    ['Manor House Lane', 10522, 20, 'NY', '', 'Dobbs Ferry'],
    ['MANOR HOUSE LN', 10522, 20, '', '', 'Dobbs Ferry'])
)
print(time.perf_counter() - start2)"""

"""a = [[1, 2], [3, 4], [5, 6]]
b = [[1, 2], [1, 3], [2, 3], [3, 4], [4, 6], [5, 6]]
union_a_b = []

a.extend(b)

for pair in a:
    if pair not in union_a_b:
        union_a_b.append(pair)
    else:
        continue

print(union_a_b)"""

"""import requests

url = "https://peekgeo.p.rapidapi.com/reverse_geocode/roof_top"

querystring = {"search_model": "roof_top", "latitude":"43.0920867","longitude":"-77.6439961","radius":"10","reverse_param": False}
print(querystring)
headers = {
    'x-rapidapi-host': "placesGeocoding.p.rapidapi.com",
    'x-rapidapi-key': "2995365d3cmshdc3df09507cf3d7p1252f5jsndbc120dd6f14"
    }

response = requests.request("GET", url, headers=headers, params=querystring)

print(response.text)"""

"""from CythonOperations import radius_arr

start = time.perf_counter()
print(radius_arr.construct_radius_arr(10, 125))
print(time.perf_counter() - start)"""

