import os
from multiprocessing import Process, Queue
from flask import Flask
from flask import request
import socket

app = Flask(__name__)

QRADAR_PORT = 514


class Log:
    def __init__(self, src_ip, dst_ip, url, timestamp=None):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.url = url
        self.timestamp = timestamp

    def format_log(self):
        return f'MONIT: src_ip={self.src_ip}'


@app.route("/")
def hello():
    return "Test page"


@app.route('/add_log/', methods=["POST"])
def add_request_source_ip():
    data = request.get_json()
    src_ip = data['src_ip']
    dst_ip = data['dst_ip']
    url = data['url']
    timestamp = data['timestamp']
    log = Log(src_ip, dst_ip, url, timestamp)
    log_queue.put(log)
    return (f'OK, log added: {log.format_log()}\n', 201)


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
        self.socket.send(bytes(f'{data}\n', "utf8"))


def send_log(client, log_queue):
    while True:
        if not log_queue.empty():
            log = log_queue.get()
            client.send_data(log.format_log())


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
