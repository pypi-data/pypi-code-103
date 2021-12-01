import requests
import pymongo
import ssl
import datetime
import time
import ast


# TODO: complete testing code for API endpoints
# TODO: debug any issues and make sure it works spotless
###DEFINE timing function at the top to used as a decorator
def time_function(function):
    def wrapper_function(*args, **kwargs):
        start = time.perf_counter()
        function(*args, **kwargs)
        total_runtime = time.perf_counter() - start
        return total_runtime

    return wrapper_function


###CLASS definitions below for unit testing capability
class SetUpDBS:

    def __init__(self, dataset, maxSize):
        self.dataset = dataset
        self.maxSize = maxSize
        self.mongo_pass = 'Barca2004!'

        self.client = pymongo.MongoClient(
            'mongodb+srv://martin_mashalov:{}@locationpoints.wi1dk.mongodb.net/test'.format(self.mongo_pass),
            maxPoolSize=maxSize,
            ssl_cert_reqs=ssl.CERT_NONE)

        self.db = self.client[self.dataset]
        self.property_collection = self.db['propLocations']
        self.account_collection = self.db['Accounts']

    def __len__(self):
        return self.account_collection.estimated_document_count()

    def __float__(self, input_case):
        if isinstance(input_case, int) or isinstance(input_case, float):
            return float(input_case)
        else:
            raise Exception("Uncorrectable Type Error")

    def __call__(self, first, last):
        account = self.account_collection.find({'$and': [{'details.firstname': first}, {'details.lastname': last}]})
        try:
            account = [i for i in account][0]
            return len(account['preferences']['properties'])
        except:
            return 0

class PeekAppEndpointTest(SetUpDBS):

    def __init__(self, dataset):
        self.maxpoolsize = 50
        self.dataset = dataset
        self.coordinates = [43.0789363, -77.6462623]
        self.property_ids = []
        super(PeekAppEndpointTest, self).__init__(self.dataset, self.maxpoolsize)

        self.property_urls = {
            'GetPropertyDetails': 'http://127.0.0.1:5000/get_property/?availability=all&house_loc=[43.0789363, -77.6462623]',
            'LoadCoordinates': 'http://127.0.0.1:5000/load_properties/?location=[43.0785005, -77.6459917]&radius=1000'
        }

        self.user_urls = {
            'AddUserProperty1': 'http://realstate-dev.us-east-1.elasticbeanstalk.com/add_user_property/?lastname=asdfjajfhksjhfkajs&firstname=uqowasfhsdfh&email=abc1@gmail.com&addr=4994 State Route 23, Windham, NY, 12494&price=3450001&bed=3&bath=3&tax=2035&area=1812&pool=no&stat=available&image=https://ap.rdcpix.com/e6588db17b627c293a40dc443dad00afl-m3631576332x.jpg, https://ar.rdcpix.com/e6588db17b627c293a40dc443dad00afl-m3631576332x.jpg&lat=42.306199&long=-74.223715&date_up=05/01/2021&year=2005',
            'AddUserProperty2': 'http://realstate-dev.us-east-1.elasticbeanstalk.com/add_user_property/?lastname=asdfjajfhksjhfkajs&firstname=uqowasfhsdfh&email=abc1@gmail.com&addr=4995 State Route 23, Windham, NY, 12494&price=3450001&bed=3&bath=3&tax=2035&area=1812&pool=no&stat=available&image=https://ap.rdcpix.com/e6588db17b627c293a40dc443dad00afl-m3631576332x.jpg, https://ar.rdcpix.com/e6588db17b627c293a40dc443dad00afl-m3631576332x.jpg&lat=42.306199&long=-74.223715&date_up=05/01/2021&year=2005',
            'AddUserSameEmailError': 'http://realstate-dev.us-east-1.elasticbeanstalk.com/add_user_property/?lastname=asdfjajfhksjhfkajs&firstname=owasfhsdfh&email=abc1@gmail.com&addr=4996 State Route 23, Windham, NY, 12494&price=3450001&bed=3&bath=3&tax=2035&area=1812&pool=no&stat=available&image=https://ap.rdcpix.com/e6588db17b627c293a40dc443dad00afl-m3631576332x.jpg, https://ar.rdcpix.com/e6588db17b627c293a40dc443dad00afl-m3631576332x.jpg&lat=42.306199&long=-74.223715&date_up=05/01/2021&year=2005',
            'AddUserDifEmailSameName': 'http://realstate-dev.us-east-1.elasticbeanstalk.com/add_user_property/?lastname=asdfjajfhksjhfkajs&firstname=uqowasfhsdfh&email=abc123@gmail.com&addr=4995 State Route 23, Windham, NY, 12494&price=3450001&bed=3&bath=3&tax=2035&area=1812&pool=no&stat=available&image=https://ap.rdcpix.com/e6588db17b627c293a40dc443dad00afl-m3631576332x.jpg, https://ar.rdcpix.com/e6588db17b627c293a40dc443dad00afl-m3631576332x.jpg&lat=42.306199&long=-74.223715&date_up=05/01/2021&year=2005',
            'GetFavoriteList': 'http://realstate-dev.us-east-1.elasticbeanstalk.com/retrieve_user_data/?email=abc1@gmail.com',
            'DelProperty': 'http://realstate-dev.us-east-1.elasticbeanstalk.com/del_property/?firstname=uqowasfhsdfh&lastname=asdfjajfhksjhfkajs&email=abc1@gmail.com&property_id='}

        self.query_collection = {
            'primary_user': {'$and': [{'details.firstname': 'uqowasfhsdfh'},
                                      {'details.lastname': 'asdfjajfhksjhfkajs'},
                                      {'details.email': 'abc1@gmail.com'}]},
            'secondary_user': {'$and': [{'details.firstname': 'uqowasfhsdfh'},
                                        {'details.lastname': 'asdfjajfhksjhfkajs'},
                                        {'details.email': 'abc123@gmail.com'}]}
        }

    # should say failed
    @staticmethod
    def AddUser_sameEmail(url):

        MetaClass = SetUpDBS('PeekDB', 50)
        account_db_length = len(MetaClass)

        with open('UnitTestFile.txt', 'a+') as unit_test_file:
            try:
                status = requests.head(url).status_code
                if 200 < status <= 300:
                    status_code = 'GOOD'
                    data = requests.get(url).json()
                    message = data['msg']
                    code = data['code']
                else:
                    status_code = 'ERROR/WRONG ID'
                    message = 'no duplicate detected, should have'
                    code = 0

            except ValueError:
                status_code = 'ERROR/WRONG ID'
                message = 'no duplicated detected, should have'
                code = 0

            new_account_db_length = len(MetaClass)
            if new_account_db_length == account_db_length:
                duplicate_added = 'NO DUP ADDED'
            else:
                duplicate_added = 'DUP ADDED, CRITICAL, SAME EMAIL'

            return 'Testing: {}; URL status(raw): {} URL status(interpretted): {} msg_line_endpoint: {} function_code: {} UserAdded?: {}'.format(
                'AddUser(SameEmailErrorCheck)',
                status,
                status_code,
                message,
                code,
                duplicate_added)

    # should say failed, use url AddUserEndpoint<1>
    @staticmethod
    def AddProp_dup(url):
        MetaClass = SetUpDBS('PeekDB', 50)
        init_favorite_len = MetaClass('uqowasfhsdfh', 'asdfjajfhksjhfkajs')

        with open('UnitTestFile.txt', 'a+') as unit_test_file:
            try:
                status = requests.head(url).status_code
                if 200 < status <= 300:
                    status_code = 'GOOD'
                    data = requests.get(url).json()
                    message = data['msg']
                    code = data['code']
                else:
                    status_code = 'ERROR/WRONG ID'
                    message = 'no duplicate detected, should have'
                    code = 0

            except ValueError:
                status_code = 'ERROR/WRONG ID'
                message = 'no duplicated detected, should have'
                code = 0

            new_favorite_len = MetaClass('uqowasfhsdfh', 'asdfjajfhksjhfkajs')
            if init_favorite_len == new_favorite_len:
                duplicate_added = 'NO DUP ADDED'
            else:
                duplicate_added = 'DUP ADDED, CRITICAL'

            return 'Testing: {}; URL status(raw): {} URL status(interpretted): {} msg_line_endpoint: {} function_code: {} UserAdded?: {}'.format(
                'AddUserEndpoint(Duplicate property addition test)',
                status,
                status_code,
                message,
                code,
                duplicate_added)

    # should add the property and succeed
    @staticmethod
    def AddUser_SameNameDifEmail(url):
        MetaClass = SetUpDBS('PeekDB', 50)
        init_account_len = len(MetaClass)

        try:
            status = requests.head(url).status_code
            print(status, 'status of AddUser_SameNameDifEmail request')
            if 200 < status <= 300:
                status_code = 'GOOD'
                data = requests.get(url).json()
                message = data['msg']
                code = data['code']
            else:
                status_code = 'ERROR/WRONG ID'
                message = 'no duplicate detected, should have'
                code = 0

        except ValueError:
            status = 400
            status_code = 'ERROR/WRONG ID'
            message = 'no duplicated detected, should have'
            code = 0

        new_account_len = len(MetaClass)
        if init_account_len == new_account_len - 1:
            duplicate_added = 'NEW USER ADDED'
        else:
            duplicate_added = 'NO USER ADDED, CRITICAL'

        return 'Testing: {}; URL status(raw): {} URL status(interpretted): {} msg_line_endpoint: {} function_code: {} UserAdded?: {}'.format(
            'AddUserEndpoint(Add another user endpoint)',
            status,
            status_code,
            message,
            code,
            duplicate_added)

    def remove_added_test_users(self, **kwargs):

        try:
            if kwargs['user_opt'] == 1:
                query = self.account_collection.find(self.query_collection['primary_user'])
                query = [i for i in query][0]

                user_id = query['details']['user_id']
                property_ids = [i['property_id'] for i in query['preferences']['properties']]

                self.account_collection.delete_one({'$and': [{'details.firstname': 'uqowasfhsdfh'},
                                                             {'details.lastname': 'asdfjajfhksjhfkajs'},
                                                             {'details.email': 'abc1@gmail.com'}]})

                self.account_collection.update_one({'Name.n': 'IDS_CHECK'}, {'$pull': {'ID_collections': user_id}})
                for prop_id in property_ids:
                    self.account_collection.update_one({'Name.n': 'IDS_CHECK'}, {'$pull': {'Property_ID_Arr': prop_id}})

            elif kwargs['user_opt'] == 2:
                query = self.account_collection.find(self.query_collection['secondary_user'])
                query = [i for i in query][0]

                user_id = query['details']['user_id']
                property_ids = [i['property_id'] for i in query['preferences']['properties']]

                self.account_collection.delete_one({'$and': [{'details.firstname': 'uqowasfhsdfh'},
                                                             {'details.lastname': 'asdfjajfhksjhfkajs'},
                                                             {'details.email': 'abc123@gmail.com'}]})

                self.account_collection.update_one({'Name.n': 'IDS_CHECK'}, {'$pull': {'ID_collections': user_id}})
                for prop_id in property_ids:
                    self.account_collection.update_one({'Name.n': 'IDS_CHECK'}, {'$pull': {'Property_ID_Arr': prop_id}})


        except ValueError or TypeError or SystemError:
            raise Exception('The removal of test users accounted an unexpected system issue.')

    def get_property_ids(self, *type_arg, **user_kwarg):

        try:
            if isinstance(type_arg[0], list):
                if user_kwarg['user_id'].lower() == 'primary':
                    query = self.account_collection.find(self.query_collection['primary_user'])
                else:
                    query = self.account_collection.find(self.query_collection['secondary_user'])
                query = [i for i in query][0]

                for property in query['preferences']['properties']:
                    if isinstance(self.property_ids, list):
                        self.property_ids.append(property['property_id'])
                    else:
                        continue

            elif isinstance(type_arg[0], tuple):
                if user_kwarg['user_id'].lower() == 'primary':
                    query = self.account_collection.find(self.query_collection['primary_user'])
                else:
                    query = self.account_collection.find(self.query_collection['secondary_user'])
                query = [i for i in query][0]

                for property in query['preferences']['properties']:
                    if isinstance(self.property_ids, list):
                        self.property_ids.append(property['property_id'])
                    else:
                        continue

                self.property_ids = tuple(self.property_ids)

            else:
                raise TypeError

        except:
            raise Exception('Exception arise within get_prop_ids.')

    def check_realtor_key_presence(self, **kwargs):

        # query the database for the coordinate and BSON -> JSON conversion completed here
        def query_database():
            query = self.property_collection.find({'location.coordinates': self.coordinates})
            query = [i for i in query][0]
            return query

        if kwargs['time'].lower() == 'before' or kwargs['time'].lower() == 'b':
            query_result = query_database()
            if query_result['properties']['Realtor_ID'] == 0 or isinstance(query_result['properties']['Realtor_ID'],
                                                                           int):
                API_status = 1
                return API_status
            else:
                API_status = 0
                return API_status

        elif kwargs['time'].lower() == 'after' or kwargs['time'].lower() == 'a':
            query_result = query_database()
            if query_result['properties']['Realtor_ID'] != 0 or isinstance(query_result['properties']['Realtor_ID'],
                                                                           int):
                API_status = 1
                return API_status
            else:
                API_status = 0
                return API_status

        else:
            raise Exception('Improper **kwargs option set')

    def test_user_endpoints(self):
        with open('UnitTestFile.txt', 'a+') as unit_test_file:

            unit_test_file.write('--------- Peek Full Unit Test: {} ---------'.format(datetime.datetime.now()))
            unit_test_file.write('\n')

            MetaClass = SetUpDBS('PeekDB', 50)
            account_db_length = len(MetaClass)

            api_DBreplacement_status = self.check_realtor_key_presence(time='b')

            # try add_user_endpoint here
            try:
                status = requests.head(self.user_urls['AddUserProperty1']).status_code
                if 200 <= status < 300:
                    status_code = 'GOOD'
                    data = requests.get(self.user_urls['AddUserProperty1']).json()
                    message = data['msg']
                    property_id = data['data']['property_id']
                else:
                    status_code = 'ERROR'
                    data = requests.get(self.user_urls['AddUserProperty1']).json()
                    message = data['msg']
                    property_id = data['data']['property_id']

            except ValueError:
                status_code = 'ERROR'
                property_id = None

            print(property_id, "user id, not property id")
            # self.property_ids.append(property_id)

            account_db_length_new = len(MetaClass)
            if account_db_length_new == account_db_length + 1:
                user_add = 'USER ADDED'
            else:
                user_add = 'USER NOT ADDED'

            new_api_DBreplacement_status = self.check_realtor_key_presence(time='a')

            if new_api_DBreplacement_status != api_DBreplacement_status:
                api_key = "API KEY REPLACED"
            else:
                api_key = "API KEY NOT REPLACED"

            unit_test_file.write(
                'Testing: {}; URL status(raw): {} URL status(interpretted): {} msg_line_endpoint: {} UserAdded?: {}, KeyChanged?: {}'.format(
                    'AddUserEndpoint',
                    status,
                    status_code,
                    message,
                    user_add,
                    api_key))
            unit_test_file.write('\n')

            # add a different property to see if the favorites list will change length by one
            favorite_length = MetaClass('uqowasfhsdfh', 'asdfjajfhksjhfkajs')
            try:
                status = requests.head(self.user_urls['AddUserProperty2']).status_code
                if 200 <= status < 300:
                    status_code = 'GOOD'
                    data = requests.get(self.user_urls['AddUserProperty2']).json()
                    message = data['msg']
                    property_id = data['data']['property_id']
                else:
                    status_code = 'ERROR'
                    data = requests.get(self.user_urls['AddUserProperty2']).json()
                    message = data['msg']
                    property_id = data['data']['property_id']
            except ValueError:
                property_id = None
                status_code = 'ERROR'

            # add the property id to the property_id list in the init method to use later for deletion
            # self.property_ids.append(property_id)

            # check if the property has been updated
            new_favorite_length = MetaClass('uqowasfhsdfh', 'asdfjajfhksjhfkajs')
            if new_favorite_length == favorite_length + 1:
                prop_add = 'PROP ADDED'
            else:
                prop_add = 'PROP NOT ADDED'

            unit_test_file.write(
                'Testing: {}; URL status(raw): {} URL status(interpretted): {} msg_line_endpoint: {} PropAdded?: {}'.format(
                    'AddUserDifferentProp',
                    status,
                    status_code,
                    message,
                    prop_add))
            unit_test_file.write('\n')

            # add the extra add user method tests here, these two fail, do not add anything
            response = self.AddUser_sameEmail(self.user_urls['AddUserSameEmailError'])
            unit_test_file.write(response)
            unit_test_file.write('\n')

            response = self.AddProp_dup(self.user_urls['AddUserProperty1'])
            unit_test_file.write(response)
            unit_test_file.write('\n')

            # this should create another user in the account db
            response = self.AddUser_SameNameDifEmail(self.user_urls['AddUserDifEmailSameName'])
            unit_test_file.write(response)
            unit_test_file.write('\n')

            # test the get_favorite_list here
            try:
                status = requests.head(self.user_urls['GetFavoriteList']).status_code
                if 200 <= status < 300:
                    status_code = 'GOOD'
                    data = requests.get(self.user_urls['GetFavoriteList']).json()
                    # print(data)
                    message = data['msg']
                    property_favs = data['properties']
                else:
                    status_code = 'ERROR'
                    data = requests.get(self.user_urls['GetFavoriteList']).json()
                    # print(data)
                    message = data['msg']
                    property_favs = data['properties']

            except ValueError:
                property_favs = []
                status_code = 'ERROR'

            # make sure the property favorites are of length 2
            favs_length = len(property_favs)
            if favs_length == 2:
                correct_length = "CORRECT LEN"
            else:
                correct_length = "INCORRECT LEN"

            unit_test_file.write(
                'Testing: {}; URL status(raw): {} URL status(interpretted): {} msg_line_endpoint: {} FavoriteLengthCorrect?: {}'.format(
                    'FavoriteListEndpoint',
                    status,
                    status_code,
                    message,
                    correct_length))

            unit_test_file.write('\n')

            # test the deletion urls here for each property_id in the arr in the init method
            self.property_ids.clear()
            self.get_property_ids([], user_id='primary')
            print(self.property_ids, type(self.property_ids))

            for prop_id in self.property_ids:
                print(prop_id)
                try:
                    status = requests.head(self.user_urls['DelProperty']).status_code
                    if 200 <= status < 300:
                        status_code = 'GOOD'
                        data = requests.get(self.user_urls['DelProperty'] + prop_id).json()
                        print(data)
                        # print(data)
                        message = data['msg']
                    else:
                        status_code = 'ERROR'
                        # print(self.user_urls['DelProperty'] + prop_id)
                        data = requests.get(self.user_urls['DelProperty'] + prop_id).json()
                        # print(data)
                        message = data['msg']

                except ValueError:
                    status_code = "ERROR"

            favorite_length = MetaClass('uqowasfhsdfh', 'asdfjajfhksjhfkajs')
            if favorite_length == 0:
                deleted_favorites = "SUCCESS"
            else:
                deleted_favorites = "FAILED"

            unit_test_file.write(
                'Testing: {}; URL status(raw): {} URL status(interpreted): {} msg_line_endpoint: {} PropAdded?: {}'.format(
                    'DelPropertyEndpoint',
                    status,
                    status_code,
                    message,
                    deleted_favorites))

            self.remove_added_test_users(user_opt=1)
            self.remove_added_test_users(user_opt=2)

            unit_test_file.write('\n')
            unit_test_file.close()

    def test_property_endpoints(self):
        with open('UnitTestFile.txt', 'a+') as unit_test_file:
            try:
                status = requests.head(self.property_urls['LoadCoordinates']).status_code
                if 200 <= status < 300:
                    status_code = 'GOOD'
                    data = requests.get(self.property_urls['LoadCoordinates']).json()
                    if isinstance(data['address_points'], list):
                        data_type = "LIST/PROPER"
                else:
                    status_code = 'ERROR'
                    data_type = 'NONLIST/IMPROPER'

            except ValueError:
                status_code = "ERROR"
                data_type = 'NONLIST/IMPROPER'

            unit_test_file.write(
                'Testing: {}; URL status(raw): {} URL status(interpretted): {} RadiusOutputType?: {}'.format(
                    'LoadRadiusCoordinates',
                    status,
                    status_code,
                    data_type))
            unit_test_file.write('\n')

            try:
                data = requests.get(self.property_urls['GetPropertyDetails']).json()
                if data['code'] == 200:
                    status_code = 'GOOD'
                    message = data['msg']
                    if len(data.keys()) > 0:
                        property_returned = "DETAILS PRESENT"
                    else:
                        property_returned = "DETAILS NULL TYPE"
                else:
                    status_code = 'ERROR'
                    message = 'no details for this property'
                    property_returned = None

            except ValueError:
                status_code = 'ERROR'
                message = 'no details for this property'
                property_returned = None

            unit_test_file.write(
                'Testing: {}; URL status(raw): {} URL status(interpretted): {} message_returned: {} PropertyReturned?: {}'.format(
                    'PropertyDetailsEndpoint',
                    status_code,
                    status_code,
                    message,
                    property_returned))

            unit_test_file.write('\n')
            unit_test_file.close()

    @time_function
    def main(self, *args, **kwargs):
        if len(args) == 0 or len(kwargs.keys()) == 0:
            self.test_user_endpoints()
            self.test_property_endpoints()
            print("done here")
        else:
            raise Exception('Uncalled for Arguments')


class PeekAPIEndpointTest(SetUpDBS):

    def __init__(self, dataset, batch_size):
        self.dataset = dataset
        self.batch_size = batch_size
        super(PeekAPIEndpointTest, self).__init__(self.dataset, 50)

        self.additional_urls = {
            'load_radius': 'http://127.0.0.1:5000/load_properties_api/?latitude=43.092541&longitude=-77.640418&radius=100',
            'polygon_search': 'http://127.0.0.1:5000/polygon_search/?edges=[[43.0863315, -77.6400726], [43.0863315, -77.6400726], [43.0824877, -77.6338292], [43.0841447, -77.639539]]',
        }

        self.reverse_geocoding_urls = {
            'reverse_single': 'http://127.0.0.1:5000/reverse_geocode/?coordinate=[43.1017166, -77.6342237]&radius=100',
            'batch_reverse': 'http://127.0.0.1:5000/batch_reverse/?coordinates=[[43.1018722, -77.6334654], [43.09245, -77.6353749], [43.0875773, -77.6383543], [43.0899153, -77.6424486], [43.0876896, -77.6440264], [43.0913689, -77.6467333], [43.0910046, -77.6455201]]&radius=10'
        }

        self.geocoding_urls = {
            'geocode_single': 'http://127.0.0.1:5000/geocoding/?address=20 Manor House Lane, Dobbs Ferry, NY, 10522&radius=10',
            'batch_geocode': 'http://127.0.0.1:5000/batch_geocoding/?addresses=["20 Manor House Lane, Dobbs Ferry, NY, 10522", "18 Manor House Lane, Dobbs Ferry, NY, 10522"]&radius=100'
        }

    def test_api(self):
        with open('UnitTestFile.txt', 'a+') as unit_test_file:
            unit_test_file.write('--------- Peek API test --------- :{}'.format(datetime.datetime.now()))
            unit_test_file.write('\n')

            # load_radius search here
            try:
                status = requests.head(self.additional_urls['load_radius']).status_code
                if 200 <= status < 300:
                    data = requests.get(self.additional_urls['load_radius']).json()

                    # there should be 8 properties returned
                    build = data['meta']['build']
                    radius_response_length = len(data['meta']['geocoded_data']['radius_array'])
                    if radius_response_length == 9:
                        message = 'RESPONSE SUCCESS'
                    else:
                        message = 'RESPONSE SUCCESS/SHORT!'

                else:
                    build = 0
                    radius_response_length = 0
                    message = 'RESPONSE FAILURE'

            except ValueError:
                build = 0
                radius_response_length = 0
                message = 'RESPONSE FAILURE'

            unit_test_file.write(
                'Testing: {}; URL status(raw): {} URL status(interpretted): {} build_id: {} RadiusResponseLength?: {}'.format(
                    'LoadRadiusEndpoint',
                    status,
                    message,
                    build,
                    radius_response_length))
            unit_test_file.write('\n')

            # polygon search test here
            try:
                status = requests.head(self.additional_urls['polygon_search']).status_code
                if 200 <= status < 300:
                    data = requests.get(self.additional_urls['polygon_search']).json()

                    # there should be 8 properties returned
                    radius_response_length = len(data['data'])
                    if radius_response_length == 8:
                        message = 'RESPONSE SUCCESS'
                    else:
                        message = 'RESPONSE SUCCESS/SHORT!'

                else:
                    radius_response_length = 0
                    message = 'RESPONSE FAILURE'

            except ValueError:
                radius_response_length = 0
                message = 'RESPONSE FAILURE'

            unit_test_file.write(
                'Testing: {}; URL status(raw): {} URL status(interpretted): {} build_id: {} ConvexResponseLength?: {}'.format(
                    'ConvexLocationEndpoints',
                    status,
                    message,
                    build,
                    radius_response_length))
            unit_test_file.write('\n')

            # reverse geocode (singular)
            try:
                status = requests.head(self.reverse_geocoding_urls['reverse_single']).status_code
                if 200 <= status < 300:
                    data = requests.get(self.reverse_geocoding_urls['reverse_single']).json()

                    # there should be 8 properties returned
                    build = data['meta']['build']
                    # print(data)
                    address = data['meta']['geocoded_data']['address_point']
                    if address == '88 Crittenden Way, Unit 2, Brighton, 14623, NY':
                        message = 'RESPONSE SUCCESS'
                    else:
                        address = None
                        build = 0
                        message = 'INCORRECT ADDRESS CONVERSION ERROR'

                else:
                    build = 0
                    address = None
                    message = 'RESPONSE FAILURE'

            except ValueError:
                build = 0
                radius_response_length = 0
                message = 'RESPONSE FAILURE'

            unit_test_file.write(
                'Testing: {}; URL status(raw): {} URL status(interpretted): {} build_id: {} SingularReverseGeocoder?: {}'.format(
                    'Reverse Geocoding Singular',
                    status,
                    message,
                    build,
                    address))
            unit_test_file.write('\n')

            # batch reverse geocoding test here ------------------------
            try:
                status = requests.head(self.reverse_geocoding_urls['batch_reverse']).status_code
                if 200 <= status < 300:
                    data = requests.get(self.reverse_geocoding_urls['batch_reverse']).json()

                    # there should be 8 properties returned
                    print(data)
                    build = data['meta']['build']
                    address_length = len(data['meta']['reverse_geocoded_data']['address_point'])
                    print(address_length)
                    if address_length == 5:
                        message = 'RESPONSE SUCCESS'
                    else:
                        address_length = 0
                        build = 0
                        message = 'NOT ENOUGH ADDRESSES'

                else:
                    build = 0
                    address_length = 0
                    message = 'RESPONSE FAILURE'

            except ValueError:
                build = 0
                radius_response_length = 0
                message = 'RESPONSE FAILURE'

            unit_test_file.write(
                'Testing: {}; URL status(raw): {} URL status(interpretted): {} build_id: {} BatchReverseGeocoder?: {}'.format(
                    'Batch Reverse Geocoding',
                    status,
                    message,
                    build,
                    address_length))
            unit_test_file.write('\n')

            # geocoding endpoint
            try:
                status = requests.head(self.geocoding_urls['geocode_single']).status_code
                if 200 <= status < 300:
                    data = requests.get(self.geocoding_urls['geocode_single']).json()

                    print(data)
                    coordinates = data['Valid Response'][0]['Coordinates']
                    if coordinates == [41.0106378, -73.8619343]:
                        message = 'RESPONSE SUCCESS'
                    else:
                        build = 0
                        message = 'INCORRECT COORDINATES'

                else:
                    build = 0
                    coordinates = [None, None]
                    message = 'RESPONSE FAILURE'

            except ValueError:
                build = 0
                coordinates = [None, None]
                message = 'RESPONSE FAILURE'

            unit_test_file.write(
                'Testing: {}; URL status(raw): {} URL status(interpretted): {} build_id: {} CoordinatesReturned?: {}'.format(
                    'geocoding singular',
                    status,
                    message,
                    build,
                    coordinates))
            unit_test_file.write('\n')

            # batch geocoder endpoint
            try:
                status = requests.head(self.geocoding_urls['batch_geocode']).status_code
                if 200 <= status < 300:
                    data = requests.get(self.geocoding_urls['batch_geocode']).json()

                    print(data)
                    coordinates = len(data['Coordinates'])
                    if coordinates == 7:
                        message = 'RESPONSE SUCCESS'
                    else:
                        build = 0
                        message = 'INCORRECT COORDINATES'

                else:
                    build = 0
                    coordinates = [None, None]
                    message = 'RESPONSE FAILURE'

            except ValueError:
                build = 0
                coordinates = [None, None]
                message = 'RESPONSE FAILURE'

            unit_test_file.write(
                'Testing: {}; URL status(raw): {} URL status(interpretted): {} build_id: {} CoordinatesReturned?: {}'.format(
                    'batch Geocoding Singular',
                    status,
                    message,
                    build,
                    coordinates))

            unit_test_file.write('\n')
            unit_test_file.write('\n')
            unit_test_file.write('\n')
            unit_test_file.close()

    # @time_function
    def main(self):
        self.test_api()


def main(dataset, batch_size):
    Peek_mobile_test = PeekAppEndpointTest(dataset)
    Peek_api_test = PeekAPIEndpointTest(dataset, batch_size)

    Peek_mobile_test.main()
    Peek_api_test.main()


#main('PeekDB', 50)

def test_endpoint_runtime():
    runtimes = []
    url = 'http://127.0.0.1:8000/load_properties_api/parcel?latitude=43.092541&longitude=-77.640418&radius=200&reverse_param=false'
    for _ in range(10):
        start = time.perf_counter()
        data = requests.get(url)
        print(data)
        runtime = time.perf_counter() - start
        runtimes.append(runtime)
    print(sum(runtimes)/len(runtimes))

#test_endpoint_runtime()
