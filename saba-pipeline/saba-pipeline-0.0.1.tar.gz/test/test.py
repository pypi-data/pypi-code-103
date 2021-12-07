# class X:
#     pass
#
#
# class Y(X):
#     pass
#
#
# class Z(Y):
#     pass
#
#
# class W(Z):
#     pass
#
#
# my_var = Z()
# t = type(my_var)
# print(issubclass(t, W))
# print(issubclass(t, Z))
# print(issubclass(t, Y))
# print(issubclass(t, X))
#


# class X:
#     def __init__(self):
#         print('hi')
#
#
# class Y(X):
#     def __init__(self):
#         super().__init__()
#         print('hello')
#
#
# class Z(Y):
#     pass
#
#
# class W(Y):
#     def __init__(self):
#         super().__init__()
#         print('OK?')
#
#
# a, b, c, d = X(), Y(), Z(), W()
from random import randint
from typing import List
from src.sabapipeline import Event, EventHandler
from src.sabapipeline import TriggerableEventBatchSource

class MyEvent(Event):
    def __init__(self, x):
        self.x = x
    def __str__(self):
        return f'({self.x})'

class X(TriggerableEventBatchSource):
    def get_event_batch(self) -> List[Event]:
        a, b = randint(1, 10), randint(1, 10)
        return [MyEvent(i) for i in range(a, a+b)]

class XEventHandler(EventHandler):
    def handle_event(self, event_to_handle: Event):
        print(event_to_handle)


x = X()
x.event_handler = XEventHandler()
for i in range(100):
    x.generate_event()
