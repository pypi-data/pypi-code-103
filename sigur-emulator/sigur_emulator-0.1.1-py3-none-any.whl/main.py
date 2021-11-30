from sigure_emulator import functions
from sigure_emulator import responses


class SigurEmulator:
    """ Класс, эмулирующий подключение по socket с реальным контроллером СКУД, имеет методы:
    send - для отправки команд, recv - для получения ответа.
    Так-же имеет метод engine, который обрабатывает ответы полученные из send и создает ответы, доступные для recv """
    def __init__(self,
                 name='SigurEmulator',
                 login="Administrator",
                 password="",
                 version="1.8",
                 points=4):
        self.name = name
        self.buffer = ''
        self.login = login
        self.password = password
        self.version = version
        self.auth = False
        self.points_dict = functions.create_points_dict(points)

    def send(self, command, *args, **kwargs):
        self.engine(command)
        return '\n{} got command: {}'.format(self.name, command)

    def engine(self, command):
        """ Обрабатывает полученную команду через send и сохраняет ответ в буффер self.buffer """
        command = command.decode()
        command = command.replace('\r\n', '')
        splitted = command.split(' ')
        command_tag = splitted[0]
        method = functions.get_method(command_tag)
        if method['status']:
            response = method['method'](*splitted, all_points_states=self.points_dict, core=self)
            self.buffer += response
            #if method['type'] == 'set_point_status' and not responses.setapinfo_incorrect_state in response:
            #    point_number = splitted[2]
            #    status = splitted[1]
            #   self.buffer += functions.add_emulated_event_buffer(point_number, status)

    def init_card_read_emulating_external(self, card_num):
        message = functions.get_emulated_event_ce_rfid_read(responses.event_ce_mask_elements['INTERNAL'], card_num)
        self.buffer += message
        return message

    def init_card_read_emulating_internal(self, card_num):
        message = functions.get_emulated_event_ce_rfid_read(responses.event_ce_mask_elements['EXTERNAL'], card_num)
        self.buffer += message
        return message


    def recv(self, *args, **kwargs):
        while True:
            if self.buffer:
                buffer = self.buffer
                self.buffer = ''
                return buffer.encode()
            else:
                pass

    def connect(self, *args, **kwargs):
        #print('\nConnecting to SigurEmulator naming {}...'.format(self.name))
        pass

