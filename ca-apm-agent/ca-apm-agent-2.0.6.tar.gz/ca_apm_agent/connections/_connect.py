__copyright__ = """
* Copyright (c) 2018 CA. All rights reserved.
*
* This software and all information contained therein is confidential and proprietary and
* shall not be duplicated, used, disclosed or disseminated in any way except as authorized
* by the applicable license agreement, without the express written permission of CA. All
* authorized reproductions must be marked with this language.
*
* EXCEPT AS SET FORTH IN THE APPLICABLE LICENSE AGREEMENT, TO THE EXTENT
* PERMITTED BY APPLICABLE LAW, CA PROVIDES THIS SOFTWARE WITHOUT WARRANTY
* OF ANY KIND, INCLUDING WITHOUT LIMITATION, ANY IMPLIED WARRANTIES OF
* MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. IN NO EVENT WILL CA BE
* LIABLE TO THE END USER OR ANY THIRD PARTY FOR ANY LOSS OR DAMAGE, DIRECT OR
* INDIRECT, FROM THE USE OF THIS SOFTWARE, INCLUDING WITHOUT LIMITATION, LOST
* PROFITS, BUSINESS INTERRUPTION, GOODWILL, OR LOST DATA, EVEN IF CA IS
* EXPRESSLY ADVISED OF SUCH LOSS OR DAMAGE.
"""
import socket
import time
import errno


class Connect:
    def __init__(self, host, port, logger):
        self.host = host
        self.port = port
        self.logger = logger
        self.sock = None

    def connect(self):
        self.logger.info('Attempt to connect with the Collector')
        try:
            self.sock = socket.create_connection((self.host, self.port))
        except Exception as e:
            self.logger.error('Unable to connect to the Collector - Check if Collector is Running')
            self.logger.debug('Exception that was raised %s', str(e))
            return False
        else:
            self.logger.info('Attempt succeeded')
            return True

    def send(self, msg):
        msg = msg + '\r\n'
        MSGLEN = len(msg)
        totalsent = 0
        sent = 0
        while totalsent < MSGLEN:
            try:
                sent = self.sock.send(msg[totalsent:].encode())
            except Exception as e:
                if sent == 0:
                    self.logger.error('SEND - Socket connection broken/closed on the other end')
                return False
            else:
                self.logger.debug('Sent Message: ' + msg[totalsent:])
                totalsent = totalsent + sent
        return True

    def receive(self, timeout=1):
        self.sock.setblocking(0)
        total_data = []
        begin = time.time()
        while True:
            # if you got some data, then break after wait sec
            if total_data and time.time() - begin > timeout:
                break
            # if you got no data at all, wait a little longer
            elif time.time() - begin > timeout * 2:
                break
            try:
                data = self.sock.recv(8192).strip()
                if data:
                    total_data.append(data.decode())
                    begin = time.time()                    
                else:
                    self.logger.error('RECEIVE - Socket closed/broken on the other end')
                    return False
            except socket.error as e:
                if e.errno != errno.EWOULDBLOCK and e.errno != errno.EAGAIN:
                    self.logger.error('RECEIVE - Unknown error at socket')
                    self.logger.debug('Exception that was raised %s', str(e))
                    return False
        self.logger.debug('Received Message: ' + ''.join(str(total_data)))
        return ''.join(map(str, total_data))

    def close(self):
        try:
            self.sock.close()
        except AttributeError:
            pass
        except Exception as e:
            self.logger.error('Unknown exception closing socket')
            self.logger.debug('Exception that was raised %s', str(e))
