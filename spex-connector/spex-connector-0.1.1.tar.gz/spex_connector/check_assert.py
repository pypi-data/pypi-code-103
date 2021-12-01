import os

IT = os.getenv('IT')
assert IT


class Ahihi(object):

    @classmethod
    def say_hello(cls):
        print("Ahihi !!!")
