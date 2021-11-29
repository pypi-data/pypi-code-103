#!/usr/bin/env python3
# -*    - coding: utf-8 -*-

"""
It provides the feature of recording images and videos from the camera.
"""

__author__ = 'ibrahim CÖRÜT'
__email__ = 'ibrhmcorut@gmail.com'

import cv2
import os
import platform
from ..Decorators import try_except
from ..Shell import print_error
from threading import Thread
from time import sleep


class Webcam:
    def __init__(self):
        self.__thread = None
        self.__camera = None
        self.__camera_out = None
        self.__camera_out_status = False
        self.connection_status = None
        self.device = None
        self.devices = None
        self.frame = None
        self.webcam_show_on_cv2 = False
        self.webcam_show_status = True  # on GUI
        self.webcam_video_out_path = None
    
    @try_except
    def get_devices(self):
        """
        Checks how many cameras are installed on the PC
        :rtype: The list returns ['None', 'Webcam Device 1', 'Webcam Device 2', ...]
        """
        self.devices = ['None']
        for index in range(33):
            try:
                if platform.system() == 'Windows':
                    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
                else:
                    cap = cv2.VideoCapture(index)
                if cap.isOpened() and cap.read()[0]:
                    self.devices.append(f'Webcam Device {index}')
                    cap.release()
                    cv2.destroyAllWindows()
            except cv2.error:
                pass
        print(f'Webcam Device List:{self.devices}')
        return self.devices

    @try_except
    def running(self):
        while self.connection_status:
            ret, self.frame = self.__camera.read()
            if ret and self.__camera_out_status:
                try:
                    self.__camera_out.write(self.frame)
                except Exception as error:
                    print(f'WEBCAM DEVICE:{self.device} WRITE PROBLEM:{error}')
            if self.webcam_show_status and self.webcam_show_on_cv2:
                cv2.imshow(f'Webcam Preview V.0.0.1 ---> Device: {self.device}', self.frame)
            else:
                # noinspection PyBroadException
                try:
                    cv2.destroyWindow(f'Webcam Preview V.0.0.1 ---> Device: {self.device}')
                except Exception:
                    pass
            cv2.waitKey(100)

    @try_except
    def disconnect(self):
        self.__camera_out_status = False
        self.connection_status = False
        if self.__thread:
            self.__thread.join()
        if self.__camera:
            self.__camera.release()
        if self.__camera_out:
            self.__camera_out.release()
        cv2.destroyAllWindows()
        self.__camera = None
        self.__thread = None
        self.frame = None
        print(f'-----> Webcam Device:{self.device} disconnection successfully.')

    @try_except
    def connect(self):
        if platform.system() == 'Windows':
            os.system('setx OPENCV_VIDEOIO_PRIORITY_MSMF 0')
        if self.device:
            if platform.system() == 'Windows':
                self.__camera = cv2.VideoCapture(int(self.device), cv2.CAP_DSHOW)
            else:
                self.__camera = cv2.VideoCapture(int(self.device))
            if self.__camera.isOpened():
                self.connection_status = True
                self.__thread = Thread(target=self.running, name='THREAD Webcam', daemon=True)
                self.__thread.start()
                sleep(0.1)
                print(f'-----> Webcam Device:{self.device} connection successfully opened.')
            else:
                print(f'-----> Webcam Device:{self.device} not opened.')
                self.disconnect()
        else:
            print(f'-----> Webcam Device:{self.device} not installed...')

    def get_frame(self):
        """
        Returns 1 frame image
        :rtype: object
        """
        if self.__camera:
            return self.frame
        return None

    def grab_image(self, path):
        """
        Used to take pictures on webcam.
        for example;
            grab_image('test.png')
        :param path: File path to save.
        :return: Return the result of the operation as boolean
        """
        try:
            cv2.imwrite(path, self.frame)
            print(f'Webcam Device:{self.device} Capture image successfully received: {path}')
            return True
        except Exception as error:
            print(f'WEBCAM DEVICE:{self.device} GRAB IMAGE PROBLEM:{error}')
            return False

    def __grab_video(self):
        try:
            width = int(self.__camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.__camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # should be written in lower case
            self.__camera_out = cv2.VideoWriter(
                self.webcam_video_out_path, fourcc, 13, (width, height), True
            )
        except Exception as error:
            print_error(error, locals())

    def grab_video(self, path=None, status='Start', second=None):
        """
        Used to record video on webcam.
        for example;
            grab_video('test.mp4', second=7)
            or
            grab_video('test2.mp4', status='Start')
            sleep(6)
            ... other process
            ... other process
            grab_video('test2.mp4', status='Stop')

        :param path: File path to save.
        :param status: If the time interval for video recording is uncertain and
                        you want to record parallel video,
                        it is necessary to call with Start / Stop.
        :param second: If recording is desired for a certain length of time
        :return: Returns video recording completion status
        """
        finish_status = False
        try:
            if str(status).lower() == 'start':
                print(f'-----> Webcam Device:{self.device} Video recording started. Path:{path}')
                self.webcam_video_out_path = path
                self.__grab_video()
                self.__camera_out_status = True
            if second and str(second).isdigit():
                print(f'-------> Sleep({second})')
                sleep(second)
                status = 'Stop'
            if str(status).lower() == 'stop':
                self.__camera_out_status = False
                if self.__camera_out:
                    self.__camera_out.release()
                sleep(0.5)
                finish_status = True
                print(
                    f'-----> Webcam Device:{self.device} Video recording stopped. '
                    f'Path:{self.webcam_video_out_path}'
                )
                self.webcam_video_out_path = None
        except Exception as error:
            print_error(error, locals())
        return finish_status
