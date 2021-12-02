# MIT License
#
# Copyright (c) 2021 Mobotx
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from concurrent import futures
import grpc
import sys, signal

import mobot._proto as proto
from ._connection import Connection

from ._assets.camera import Camera
from ._assets.chassis import Chassis
from ._assets.accelerometer import Accelerometer
from ._assets.gyroscope import Gyroscope
from ._assets.magnetometer import Magnetometer
from ._assets.flashlight import Flashlight
from ._assets.speak import Speak
from ._assets.listen import Listen

from mobot.utils.network import _get_ip_address
from mobot.utils.logging import _get_logger

class Agent:
    def __init__(self):
        self.logger = _get_logger()

        signal.signal(signal.SIGINT, self.__sigint_handler)
        signal.signal(signal.SIGALRM, self.__sigint_handler)

        try:
            ip = _get_ip_address()
        except:
            self.logger.error("Not Connected to any network!")
            sys.exit()

        self.__server = grpc.server(futures.ThreadPoolExecutor(max_workers=30))
        self.__server.add_insecure_port(f'{ip}:50052')

        self.__connection = Connection(ip, self.logger)

        self.camera = Camera(self.logger, self.__connection)
        proto.camera_pb2_grpc.add_CameraServicer_to_server(self.camera, self.__server)

        self.chassis = Chassis(self.logger, self.__connection)
        proto.chassis_pb2_grpc.add_ChassisServicer_to_server(self.chassis, self.__server)

        self.accelerometer = Accelerometer(self.logger, self.__connection)
        proto.accelerometer_pb2_grpc.add_AccelerometerServicer_to_server(self.accelerometer, self.__server)

        self.gyroscope = Gyroscope(self.logger, self.__connection)
        proto.gyroscope_pb2_grpc.add_GyroscopeServicer_to_server(self.gyroscope, self.__server)

        self.magnetometer = Magnetometer(self.logger, self.__connection)
        proto.magnetometer_pb2_grpc.add_MagnetometerServicer_to_server(self.magnetometer, self.__server)

        self.flashlight = Flashlight(self.logger, self.__connection)
        proto.flashlight_pb2_grpc.add_FlashlightServicer_to_server(self.flashlight, self.__server)

        self.speak = Speak(self.logger, self.__connection)
        proto.speak_pb2_grpc.add_SpeakServicer_to_server(self.speak, self.__server)

        self.listen = Listen(self.logger, self.__connection)
        proto.listen_pb2_grpc.add_ListenServicer_to_server(self.listen, self.__server)

        self.__actuators = [("chassis", self.chassis),\
                ("flashlight", self.flashlight),\
                ("speak", self.speak)]

    def start(self):
        self.__server.start()
        self.__connection.attach()
        if self.__wait_until_available():
            self.on_start()

    ## Waits until all the actuators that are enabled is available
    def __wait_until_available(self):
        for actuator_name, actuator in self.__actuators:
            if actuator._is_enabled():
                self.logger.info(f"Waiting for {actuator_name} to be available...")
                if actuator.wait_until_available():
                    self.logger.info(f"{actuator_name} available!")
                else:
                    return False
        return True

    def on_start(self):
        pass

    def ok(self):
        return self.__connection.attach_brain_iterator.is_active()

    def terminate(self):
        self.__sigint_handler(signal.SIGINT, 0)

    def __sigint_handler(self, signum, frame):
        if signum == signal.SIGINT or signum == signal.SIGALRM:
            self.__server.stop(None)
            self.__connection.detach()
