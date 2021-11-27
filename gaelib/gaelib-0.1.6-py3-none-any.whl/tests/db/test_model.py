"""
    This module defines the testcases for the Model class.
"""
from gaelib.tests.base import BaseUnitTestCase

from .model import Test


class ModelUnitTestCase(BaseUnitTestCase):
    
    longMessage = False

    def create_object(self,**kwargs):
        obj = Test(**kwargs)
        return obj

    def test_passing_an_already_set_key_behaviour(self):
        #adding a key in the db to check with
        key = Test.generate_key('set_key_behaviour')
        model = Test(key = key, string1 = 'value1')
        model.put()      

        #passing the same key again to see the behaviour
        model = Test(key = key)
        self.assertTrue(model.retrieved(),"Key not found") 
    
    def test_key_str_behaviour(self):
        model = Test(key_str = 'key_str_behaviour')
        self.assertIsNotNone(model.key(), "Failed to generate key from key_str")
    
    def test_entity_as_keyword_behaviour(self): 
        model = Test(entity = self.create_object(string1 = 'value1', string2 = 'value2'))
        self.assertIsNotNone(model.__entity__, "Failed to create entity")

    def test_no_id_behaviour(self):
        model = Test()
        self.assertIsNotNone(model.key(), "Failed to generate key")
    
    def test_check_default_properties(self):
        model = self.create_object()
        attributes = ['string1','string2', 'int1', 'float1', 'bool1']
        for attribute in attributes:
            self.assertIsNone(model.__getattribute__(attribute), "Default value not none for attribute: {}".format(attribute))

    def check_keywords_passed(self, **kwargs):
        model = Test(**kwargs)
        model.put()
        for key, val in kwargs.items():
            self.assertEqual(model.__getattribute__(key),val, "Failed for key-value pair {} : {}".format(key,val))
      
    def test_check_keywords_passed(self):
        self.check_keywords_passed(string1 = 'one', string2 = 'two')

    def test_check_validation_of_props(self):
        self.assertRaises(ValueError, self.create_object, string1 = '123', string2 = 123, int1 = 123.40, float1 = True, bool1 = 123)

    def test_check_update_and_put(self):
        #checking put
        key = Test.generate_key('put and update')
        self.clear_database()

        model = Test(key = key, string1 = 'test_set_1')
        model.put()
        #model.retrieved() won't work here because the above instance of model is for creating the entity
        #and in that case self.__retrieved__ is set to false
        #We need to create another instance of the model with the same key and
        #then check for model.retrieved()
        model = Test(key = key)
        self.assertTrue(model.retrieved(),"Put failed")

        #checking update
        model.update(string1 = 'test_set_2')
        model.put()

        self.assertEqual(model.__getattribute__('string1'), 'test_set_2', "Update Failed")
        
    def test_check_delete(self):
        key = Test.generate_key('delete')
        #creatng a record to be deleted
        model = Test(key = key, string1 = "This record will be deleted")
        model.put()
        model = Test(key = key)
        self.assertTrue(model.retrieved(), "Failed to create entity")
        model.delete()
        model = Test(key = key)
        self.assertFalse(model.retrieved(), "Failed to delete key")
        
    def test_query(self):
        #create records to be fetched
        model = Test(key_str = 'record1', string1 = '123', string2 = '456', int1 = 111)
        model.put()
        model = Test(key_str = 'record2', string1 = '123', string2 = '456', int1 = 113)
        model.put()
        model = Test(key_str = 'record3', string1 = '123', string2 = '456', int1 = 112)
        model.put()

        #fetch records
        model = Test()
        q = model.query()
        q.add_filter('string1', '=', '123')
        q.add_filter('int1', '>', 111)
        q.assign_order('-int1') #descending
        last_value = 200
        for obj in q.fetch():
            self.assertGreaterEqual(last_value,obj.int1, "Failed to order items in result")
            last_value = obj.int1
        self.assertEquals(len(q.fetch()), 2, "Failed to fetch. Fetched {} instead of 2 items".format(len(q.fetch())))

    def test_retrieve(self):
        model = Test(key_str = 'record1', string1 = '123', string2 = '456', int1 = 111)
        model.put()
        model = Test(key_str = 'record2', string1 = '123', string2 = '456', int1 = 112)
        model.put()
        model = Test(key_str = 'record3', string1 = '123', string2 = '456', int1 = 113)
        model.put()
        model = Test(key_str = 'record3', string1 = '123', string2 = '456', int1 = 114)
        model.put()

        model = Test()

        #testing for key_str        
        items = model.retrieve(key_strs = ['record1'])
        self.assertEquals(items[0].int1, 111, "Failed to retrieve using key_str")

        #testing for filters, order and limit
        limit = 2
        items = model.retrieve(filters=[('string1', '=', '123'), ('int1', '>', 111)], order = '-int1', limit = limit)
        last_value = 200
        for obj in items:
            self.assertGreater(obj.int1, 111, "Failed to apply filter")
            self.assertEquals(obj.string1,'123', "Failed to apply filter")
            self.assertGreaterEqual(last_value,obj.int1, "Failed to order items")
            last_value = obj.int1
        self.assertEquals(len(items),limit, "Failed to apply limit. Fetched {} instead of {} items".format(len(items),limit))
