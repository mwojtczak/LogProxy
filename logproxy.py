import logging
import os
import socket
from multiprocessing import Process, Queue

from flask import Flask, request

app = Flask(__name__)

QRADAR_PORT = 514

logger = logging.getLogger(__name__)


@app.route("/")
def hello():
    return "Welcome to the home page of LogProxy server."


@app.route("/add_log/", methods=["POST"])
def add_request_source_ip():
    print('Logging request arrived')
    data = request.get_json()
    log = data["log"]
    log_queue.put(log)
    print(f'Log added: {log}')
    return (f"Log added: {log}\n", 201)


class SyslogClient:
    TCP_TIMEOUT = 10
    TCP_IDLE_AFTER_SECONDS = 2
    TCP_INTERVAL_SECONDS = 3
    TCP_MAX_FAILS = 5

    def __init__(self, server_ip, port):
        self.server_ip = server_ip
        self.port = port
        self.socket = None
        self.create_connection()

    def create_connection(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.TCP_TIMEOUT)
        sock.connect((self.server_ip, self.port))
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, self.TCP_IDLE_AFTER_SECONDS)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, self.TCP_INTERVAL_SECONDS)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, self.TCP_MAX_FAILS)
        self.socket = sock

    def _recover_socket(self):
        print("Recovering socket")
        if self.socket:
            self.socket.close()
        self.create_connection()

    def send_data(self, data):
        try:
            sent = self.socket.send(bytes(f"{data}\n", "utf8"))
            if sent <= 0:
                print(f"Error sending message {data}, restoring connection")
                self._recover_socket()
            else:
                print(f"Successfully transmitted {data}")
        except socket.error as e:
            self._recover_socket()
            self.send_data(data)


def send_log(client):
    while True:
        if not log_queue.empty():
            log = log_queue.get()
            client.send_data(log)


if __name__ == "__main__":
    log_queue = Queue()
    QRADAR_IP = os.environ["QRADAR_IP"]
    QRADAR_PORT = os.environ.get("QRADAR_PORT") or QRADAR_PORT
    try:
        qradar_client = SyslogClient(QRADAR_IP, QRADAR_PORT)
    except socket.error as e:
        logger.critical(f"Cannot connect to {QRADAR_IP}:{QRADAR_PORT} due to {e}, exiting")
        exit(1)
    http_server = Process(target=app.run, kwargs={"host": "0.0.0.0", "port": 8080})
    syslog_client = Process(target=send_log, args=(qradar_client,))
    http_server.start()
    syslog_client.start()
