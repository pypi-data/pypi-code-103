#!/usr/bin/env python

import grpc

from .proto import gateway_pb2_grpc, gateway_pb2

addr = "forecasts.anko-investor.com:443"
ua = "github.com/anglo-korean/anko-python-sdk#0.1.0"

class InvalidForecast(Exception):
    super

class Client():
    def __init__(self, token, ident):
        '''
        Create new connection
        '''
        self.auth = [('authorization', f'bearer {token}')]

        m = gateway_pb2.Metadata()
        m.ua = ua

        t = gateway_pb2.Tag()
        t.key =  'Identifier'
        t.value = ident

        m.tags.insert(0, t)
        self.tags = m

        self.__connect()


    def __connect(self):
        chan = grpc.secure_channel(addr, grpc.ssl_channel_credentials())

        self.conn = gateway_pb2_grpc.ForecastsStub(chan)


    def __reset_stream(self):
        self.stream = self.conn.Stream(self.tags, metadata=self.auth)
        self.count = 0


    def __iter__(self):
        self.__reset_stream()

        return self


    def __next__(self):
        self.count += 1

        try:
            f = next(self.stream)
            if self.count == 1:
                if not f.id == 'dummy-forecast':
                    raise InvalidForecast('expected dummy forecast')

                return

            return f

        except grpc.RpcError as e:
            self.__reset_stream()

        except Exception as e:
            print(e)
            print(type(e))
            raise e
