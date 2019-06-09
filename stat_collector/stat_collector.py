import datetime
import functools
import json
from functools import lru_cache

import flask
import requests

LOG_FORMAT = "LOGPROXY:: src_ip={src_ip} timestamp={timestamp} url={url}"


class RequestScrapper:
    def __init__(self, log_proxy_ip, log_proxy_port, log_format=None):
        self.log_proxy_ip = log_proxy_ip
        self.log_proxy_port = log_proxy_port
        self.log_format = log_format or LOG_FORMAT
        self.session = requests.session()

    @property
    @lru_cache(None)
    def logproxy_endpoint(self):
        return f"http://{self.log_proxy_ip}:{self.log_proxy_port}/add_log/"

    @staticmethod
    def _gather_data(request):
        return {
            "src_ip": request.remote_addr,
            "url": request.url,
            "timestamp": datetime.datetime.now().timestamp(),
        }

    def _format_log(self, data):
        return self.log_format.format(**data)

    def send_log(self, data):
        log = self._format_log(data)
        headers = {"Content-type": "application/json"}
        r = self.session.post(
            self.logproxy_endpoint, data=json.dumps({"log": log}), headers=headers
        )
        if r.status_code != 201:
            print("Sending log failed")

    def log(self, func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            request = flask.request
            data = self._gather_data(request)
            self.send_log(data)
            return func(*args, **kwargs)

        return inner
