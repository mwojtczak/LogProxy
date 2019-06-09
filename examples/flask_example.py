"""
This is an example usage of log_collector module inside Flask application.

To run enter commands:
pip install -r requirements.txt
python3.6 flask_example.py

There are 3 steps required to use stat collector, assuming LogProxy is deployed and available at 0.0.0.0:8080.
1. import library
from log_collector import log_collector
2. initialise Request scrapper with LogProxy ip address and port number
scrapper = log_collector.RequestScrapper(LOPPROXY_IP, LOGPROXY_PORT)
3. decorate view method to send statistics of given endpoint
@scrapper.log
"""
import os.path
import sys

from flask import Flask

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
)
from log_collector import log_collector

app = Flask(__name__)

LOGPROXY_IP = "0.0.0.0"
LOGPROXY_PORT = 8080

scrapper = log_collector.LogCollector(LOGPROXY_IP, LOGPROXY_PORT)


@app.route("/")
@scrapper.log
def main():
    return "Main page"


@app.route("/test/")
@scrapper.log
def test():
    return "Test page"


if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
