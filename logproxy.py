import os
from multiprocessing import Process, Queue
from flask import Flask
from flask import request
import socket

app = Flask(__name__)

QRADAR_PORT = 514


@app.route("/")
def hello():
    return "Welcome to the home page of LogProxy server."


@app.route('/add_log/', methods=["POST"])
def add_request_source_ip():
    data = request.get_json()
    log = data['log']
    log_queue.put(log)
    return (f'Log added: {log}\n', 201)


class SyslogClient:
    def __init__(self, server_ip, port):
        self.server_ip = server_ip
        self.port = port
        self.socket = self.create_connection()

    def create_connection(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_ip, self.port))
        return s

    def send_data(self, data):
        res = self.socket.send(bytes(f'{data}\n', "utf8"))
        if res <= 0:
            print(f"Error sending message {data}")


def send_log(client, log_queue):
    while True:
        if not log_queue.empty():
            log = log_queue.get()
            client.send_data(log)


if __name__ == '__main__':
    log_queue = Queue()
    QRADAR_IP = os.environ['QRADAR_IP']
    try:
        qradar_client = SyslogClient(QRADAR_IP, QRADAR_PORT)
    except socket.error as e:
        print(f"Cannot connect to {QRADAR_IP}:{QRADAR_PORT} due to {e}, exiting")
        exit(1)
    http_server = Process(target=app.run, kwargs={"host": '0.0.0.0', "port": 8080})
    syslog_client = Process(target=send_log, args=(qradar_client, log_queue))
    http_server.start()
    syslog_client.start()
