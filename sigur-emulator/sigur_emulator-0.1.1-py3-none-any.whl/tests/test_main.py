import unittest
from sigure_emulator.main import SigurEmulator
from sigure_emulator import responses

class TestMain(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sigur_emulator = SigurEmulator()

    def test_get_all_points_status(self):
        pass

    def test_send(self):
        command = b'GETAPINFO 3\r\n'
        response = self.sigur_emulator.send(command)
        response_must = '\n{} got command: {}'.format(self.sigur_emulator.name, command)
        self.assertEqual(response_must, response)

    def test_auth_succes(self):
        command = b'"LOGIN" 1.8 "Administrator" ""\r\n'
        self.sigur_emulator.send(command)
        response = self.sigur_emulator.recv()
        response = response.decode()
        response_must = responses.auth_success
        self.assertEqual(response, response_must)

    def test_auth_fail(self):
        command = b'LOGIN 1.8 "Administrator12" ""\r\n'
        self.sigur_emulator.send(command)
        response = self.sigur_emulator.recv()
        response = response.decode()
        response_must = responses.auth_fail
        self.assertEqual(response, response_must)

    def test_auth_fail_version(self):
        command = b'LOGIN 1.999 "Administrator" ""\r\n'
        self.sigur_emulator.send(command)
        response = self.sigur_emulator.recv()
        response = response.decode()
        response_must = responses.auth_fail_version
        self.assertEqual(response, response_must)

    def test_get_point_info_fail(self):
        command = b'GETAPINFO 5\r\n'
        self.sigur_emulator.send(command)
        response = self.sigur_emulator.recv()
        response = response.decode()
        response_must = responses.getapinfo_unknown_point
        self.assertEqual(response, response_must)

    def test_get_point_info_success(self):
        command = b'GETAPINFO 3\r\n'
        self.sigur_emulator.send(command)
        response = self.sigur_emulator.recv()
        response = response.decode()
        response_must = 'APINFO ID 3 NAME "GATE-EXIT" ZONEA 0 ZONEB 0 STATE ONLINE_LOCKED OPENED\r\n'
        self.assertEqual(response, response_must)

    def test_setapmode_success(self):
        command = b'SETAPMODE UNLOCKED 3\r\n'
        self.sigur_emulator.send(command)
        response = self.sigur_emulator.recv()
        response = response.decode().split('\r\n')[0]
        response_must = responses.setapinfo_success
        self.assertEqual(response, response_must.split('\r\n')[0])

    def test_setapmode_failed(self):
        command = b'SETAPMODE UNLOCKEDINCORRECT 3\r\n'
        self.sigur_emulator.send(command)
        response = self.sigur_emulator.recv()
        response = response.decode()
        response_must = responses.setapinfo_incorrect_state
        self.assertEqual(response, response_must)

    def test_subscribe(self):
        command = b'"SUBSCRIBE" CE\r\n'
        self.sigur_emulator.send(command)
        response = self.sigur_emulator.recv()
        response = response.decode()
        response_must = responses.subscribe_success
        self.assertEqual(response, response_must)

    def test_rfid_emulate(self):
        self.sigur_emulator.init_card_read_emulating_external('FFFF000134')
        response = self.sigur_emulator.recv()


    def test_connection(self):
        self.sigur_emulator.connect()
        data = self.sigur_emulator.recv(1024)
        print(data)



if __name__ == '__main__':
    unittest.main()
