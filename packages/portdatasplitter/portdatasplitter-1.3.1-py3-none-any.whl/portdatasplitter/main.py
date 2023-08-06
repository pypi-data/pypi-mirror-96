import socket
import threading
from serial import Serial
import serial.tools.list_ports
from time import sleep
from portdatasplitter import settings as s

class PortDataSplitter:
    """ Сервер для прослушивания порта port_name (USB, COM),
     и переотправки данных подключенным к нему клиентам (Clients)."""
    def __init__(self, ip, port, port_name='/dev/ttyUSB0', debug=False, device_name='unknown'):
        self.show_print()
        self.device_name = device_name
        self.debug = debug
        self.port_name = port_name
        self.subscribers = []
        self.data_list = [s.no_data_code]
        self.server_ip = ip
        self.server_port = port

    def get_all_connected_devices(self):
        # Показать все подключенные к этому компьютеру устройства
        ports = serial.tools.list_ports.comports()
        self.show_print('\nAll connected devices:')
        for port in ports:
            self.show_print('\t', port)
        return ports

    def get_device_name(self):
        # Вернуть заданный этому устройству имя
        return self.device_name

    def start(self):
        """ Запустить работу PortDataSplitter"""
        # Создать сервер рассылки
        self.create_server(self.server_ip, self.server_port)
        # Запустить параллельный поток, который будет принимать клиентов
        threading.Thread(target=self.connection_reciever_loop, args=()).start()
        # Запустить параллельный поток, который отправляет данные из self.data_list
        threading.Thread(target=self.sending_thread, args=(1,)).start()
        # Запустить основной поток, слушаюший заданный порт и отправляющий эти данные клиентам
        self._mainloop()

    def sending_thread(self, timing=1):
        # Поток отправки показаний весов
        while True:
            sleep(timing)
            self.send_data(self.data_list[-1])

    def create_server(self, ip, port):
        """ Создать сервер"""
        self.show_print('Creating {} server'.format(self.device_name))
        self.serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serv.bind((ip, port))
        self.serv.listen(10)

    def connection_reciever_loop(self):
        # Отдельный поток, принимающий подключения и добавляющий их в список self.subscribers для дальнейшней
        # работы
        while True:
            self.show_print('\nWaiting for client...')
            conn, addr = self.serv.accept()
            self.subscribers.append(conn)
            self.show_print('\tGot new client! From IP:', conn.getpeername()[0])

    def send_data(self, data, *args, **kwargs):
        # Отправить данные по клиентам
        for conn in self.subscribers:
            try:
                conn.send(data)
            except:
                # Если данные отправить клиенту не удалось, удалить клиента из списка подписчиков
                self.show_print('\tFailed to send data to client')
                self.subscribers.remove(conn)

    def make_str_tuple(self, msg):
        # Перед отправкой данных в стандартный поток вывывода форматировать
        return ' '.join(map(str, msg))

    def show_print(self, *msg, debug=False):
        # Отправка данных в стандартный поток выводы
        msg = self.make_str_tuple(msg)
        if debug and self.debug:
            print(msg)
        elif not debug:
            print(msg)

    def _mainloop(self):
        # Основной цикл работы программы, слушает порт и передает данные клиентам
        self.show_print('\nЗапущен основной цикл отправки весов')
        # Нужно подождать около 5 секунд после запуска всего компа
        sleep(5)
        self.port = Serial(self.port_name, bytesize=8, parity='N', stopbits=1, timeout=1, baudrate=9600)
        while True:
            data = self.port.readline()
            self.show_print(data, debug=True)
            if data:
                # Если есть данные проверить их и добавить в список отправки data_list
                data = self.check_data(data)
                self.prepare_data_to_send(data)
            else:
                 self.reconnect_logic()

    def check_data(self, data):
        self.show_print('Checking data in {}'.format(self.device_name), debug=True)
        return data

    def prepare_data_to_send(self, data):
        # Подготовить данные перед отправкой
        self.data_list = self.data_list[-15:]
        self.data_list.append(data)

    def reconnect_logic(self):
        # Логика, реализуемая при выключении терминала
        self.show_print('Терминал выключен!')
        self.port.close()
        self._mainloop()