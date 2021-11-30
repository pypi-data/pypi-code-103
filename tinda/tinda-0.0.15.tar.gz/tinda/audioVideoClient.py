

import socket
import pickle
import struct
import threading
import cv2
import pyautogui
import numpy as np  






# ----------- AUDIO -----------
class AudioOut:
    def __init__(self, host, port, audio_format=pyaudio.paInt16, channels=1, rate=44100, frames_chunk=4096):
        self.__host = host
        self.__port = port
        self.__audio_format = audio_format
        self.__channels = channels
        self.__rate = rate
        self.__frames_chunk = frames_chunk
        self.__send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__audio = pyaudio.PyAudio()
        self.__running = False
    def start(self):
        if self.__running:
            print('Streating Audio.')
        else:
            self.__running = True
            thread = threading.Thread(target=self.__clientStream)
            thread.start()
    def stop(self):
        if not self.__running:
            self.__running = False
        else:
            print('Client stream not found.')
    def __clientStream(self):
        self.__send_socket.connect((self.__host, self.__port))
        self.__stream = self.__audio.open(format=self.__audio_format, channels=self.__channels, rate=self.__rate, input=True, frames_per_buffer=self.__frames_chunk)
        while self.__running:
            self.__send_socket.send(self.__stream.read(self.__frames_chunk))

class AudioIn:
    def __init__(self, host, port, slots=8, audio_format=pyaudio.paInt16, channels=1, rate=44100, frames_chunk=4096):
        self.__host = host
        self.__port = port
        self.__slots = slots    
        self.__usedSlots = 0
        self.__audio_format = audio_format
        self.__channels = channels
        self.__rate = rate
        self.__frames_chunk = frames_chunk
        self.__audio = pyaudio.PyAudio()
        self.__serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__serverSocket.bind((self.__host, self.__port))
        self.__block = threading.Lock()
        self.__running = False
    def start(self):
        if self.__running:
            print('Streating Audio.')
        else:
            self.__running = True
            self.__stream = self.__audio(format=self.__audio_format, channels=self.__channels, rate=self.__rate, output=True, frames_per_buffer=self.__frames_chunk)
            thread = threading.Thread(target=self.__serverListening)
            thread.start()
    def __serverListening(self):
        self.__serverSocket.listen()
        while self.__running:
            self.block.acquire()
            connection, address = self.__serverSocket.accept()
            if self.__usedSlots >= self.__slots:
                print('Audio slots full.')
                connection.close()
                self.__block.release()
                continue
            else:
                self.__usedSlots += 1
            self.__block.release()
            thread = threading.Thread(target=self.__clientConnection, args=(connection, address,))
            thread.start()
    def __clientConnection(self, connection, address):
        while self.__running:
            data = connection.recv(self.__frames_chunk)
            self.__stream.write(data)
    def stop(self):
        if not self.__running:
            self.__running = False
            closingConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            closingConnection.connect((self.__host, self.__port))
            closingConnection.close()
            self.__block.acquire()
            self.__serverSocket.close()
            self.__block.release()
        else:
            print('Server stream not found.')

# ----------- VIDEO -----------
class StreamingServer:
    def __init__(self, host, port, slots=8, quitKey='q'):
        self.__host = host
        self.__port = port
        self.__slots = slots
        self.__usedSlots = 0
        self.__quitKey = quitKey
        self.__block = threading.Lock()
        self.__serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__initSocket()
    def __initSocket(self):
        self.__serverSocket.bind((self.__host, self.__port))
    def start(self):
        if self.__running:
            print('Streating running.')
        else:
            self.__running = True
            serverThread = threading.Thread(target=self.__serverListening)
            serverThread.start()
    def __serverListening(self):
        self.__serverSocket.listen()
        while self.__running:
            self.__block.acquire()
            connection, address = self.__serverSocket.accept()
            if self.__usedSlots >= self.__slots:
                print('Video slots full.')
                connection.close()
                self.__block.release()
                continue
            else:
                self.__usedSlots += 1
            self.__block.release()
            thread = threading.Thread(target=self.__clientConnection, args=(connection, address,))
            thread.start()
    def stop(self):
        if not self.__running:
            self.__running = False
            closingConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            closingConnection.connect((self.__host, self.__port))
            closingConnection.close()
            self.__block.acquire()
            self.__serverSocket.close()
            self.__block.release()
        else:
            print('Server stream not found.')
    def __clientConnection(self, connection, address):
        loadSize = struct.calcsize('>L')
        data = b""
        while self.__running:
            breakLoop = False
            while len(data) < loadSize:
                x = connection.recv(4096)
                if x == b'':
                    connection.close()
                    self.__usedSlots -= 1
                    breakLoop = True
                    break
            if breakLoop:
                break
            messagePackSize = data[:loadSize]
            data = data[loadSize:]
            messageSize = struct.unpack('>L', messagePackSize)[0]
            while len(data) < messageSize:
                data += connection.recv(4096)
            frameData = data[:messageSize]
            data = data[messageSize:]
            frame = pickle.loads(frameData, fix_imports=True, encoding="bytes")
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            cv2.imshow(str(address), frame)
            if cv2.waitKey(1) & 0xFF == ord(self.__quitKey):
                connection.close()
                self.__usedSlots -= 1
                break

class StreamClient:
    def __init__(self, host, port):
        self.__host = host
        self.__port = port
        self.__running = False
        self.__clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def __configure(self):
        self.__encoding_paramerters = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    def _getFrame(self):
        return None
    def __cleanup(self):
        cv2.destroyAllWindows()
    def __clientStream(self):
        self.__clientSocket.connect((self.__host, self.__port))
        while self.__running:
            frame = self._getFrame()
            result, frame = cv2.imencode('.jpg', frame, self.__encoding_paramerters)
            data = pickle.dumps(frame, 0)
            size = len(data)
            try:
                self.__clientSocket.sendall(struct.pack('>L', size) + data)
            except ConnectionAbortedError:
                self.__running = False
            except ConnectionResetError:
                self.__running = False
            except BrokenPipeError:
                self.__running = False
        self.__cleanup()
    def start(self):
        if self.__running:
            print('Stream running.')
        else:
            self.__running = True
            clientThread = threading.Thread(target=self.__clientStream)
            clientThread.start()
    def stop(self):
        if not self.__running:
            self.__running = False
        else:
            print('Stream not found.')

class CameraClient(StreamClient):
    def __init__(self, host, port, x_resolution=1024, y_resolution=576):
        super().__init__(host, port)
        self.__x_resolution = x_resolution
        self.__y_resolution = y_resolution
        self.__camera = cv2.VideoCapture(0)
        super(CameraClient, self).__init__(host, port)
    def __configure(self):
        self.__camera.set(3, self.__x_resolution)
        self.__camera.set(4, self.__y_resolution)
        super(CameraClient, self).__configure()
    def _getFrame(self):
        x, frame = self.__camera.read()
        return frame
    def __cleanup(self):
        self.__camera.release()
        cv2.destroyAllWindows()

class VideoClient(StreamClient):
    def __init__(self, host, port, video, loop=True):
        self.__video = cv2.VideoCapture(video)
        self.__loop = loop
        super(VideoClient, self).__init__(host, port)
    def __configure(self):
        self.__video.set(3, 1024)
        self.__video.set(4, 576)
        super(VideoClient, self).__configure()
    def _getFrame(self):
        x, frame = self.__video.read()
        return frame
    def __cleanup(self):
        self.__video.release()
        cv2.destroyAllWindows()

class ScreenSharingClient(StreamClient):
    def __init__(self, host, port, x_resolution=1024, y_resolution=576):
        self.__x_resolution = x_resolution
        self.__y_resolution = y_resolution
        super(ScreenSharingClient, self).__init__(host, port)
    def _getFrame(self):
        screen = pyautogui.screenshot()
        frame = np.array(screen)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.__x_resolution, self.__y_resolution))
        return frame


import tkinter as tk
import requests
import socket

# get local ip address
def get_ip():
    # os.system('ifconfig')
    # below requires socket library
    localIP = socket.gethostbyname(socket.gethostname())
    # this is the private ip address.
    # to get the public ip address, you can use the following website:
    # http://ip.42.pl/
    # myip.is is another website that gives you the public ip address.
    # to do it here, we'll also need requests library.
    publicIP = requests.get('http://ip.42.pl/raw').text
    x = (f"Local ip address is: {localIP}\nPublic ip address is: {publicIP}")
    # print(x)
    return [localIP, publicIP]

# Button fuctions for below GUI
def startListening():
    localIP = socket.gethostbyname(socket.gethostname())
    streaming_server_port = 9999
    server = StreamingServer(localIP, streaming_server_port)
    receiver_port = 9998
    receiver = AudioIn(localIP, receiver_port)
    thread_one = threading.Thread(target=server.start)
    thread_two = threading.Thread(target=receiver.start)
    thread_one.start()
    thread_two.start()

def cameraStream():
    camera_client = CameraClient(text_target_ip.get(1.0, 'end-1c'), 7777)
    thread_three = threading.Thread(target=camera_client.start)
    thread_three.start()

def screenSharingStream():
    screen_sharing_client = ScreenSharingClient(text_target_ip.get(1.0, 'end-1c'), 7777)
    thread_four = threading.Thread(target=screen_sharing_client.start)
    thread_four.start()

def audioStream():
    audio_client = AudioOut(text_target_ip.get(1.0, 'end-1c'), 7778)
    thread_five = threading.Thread(target=audio_client.start)
    thread_five.start()























# GUI
window = tk.Tk()
window.title("Video Call")
window.geometry('300x200')

label_target_ip = tk.Label(window, text="Target IP:")
label_target_ip.pack()

text_target_ip = tk.Text(window, height=1)
text_target_ip.pack()

btn_listen = tk.Button(window, text="Listen", width=50, command=startListening)
btn_listen.pack(anchor=tk.CENTER, expand=True)

btn_camera = tk.Button(window, text="Start Camera stream", width=50, command=cameraStream)
btn_camera.pack(anchor=tk.CENTER, expand=True)

btn_screen = tk.Button(window, text="Start screen sharing", width=50, command=screenSharingStream)
btn_screen.pack(anchor=tk.CENTER, expand=True)

btn_audio = tk.Button(window, text="Start Audio Stream", width=50, command=audioStream)
btn_audio.pack(anchor=tk.CENTER, expand=True)

window.mainloop()

# other end needs to be on different ports for this to work.
# if you want to use the same port for both, you need to use a different ip address.
