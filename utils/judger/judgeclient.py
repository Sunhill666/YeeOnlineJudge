import threading

import requests
from django.conf import settings


def synchronous_lock(func):
    def wrapper(*args, **kwargs):
        with threading.Lock():
            return func(*args, **kwargs)

    return wrapper


class JudgeClient:
    authn_token = None
    authz_token = None
    endpoint = None
    session = None
    _instance_lock = threading.Lock()

    # 线程安全单例模式
    def __new__(cls, *args, **kwargs):
        if not hasattr(JudgeClient, '_instance'):
            with JudgeClient._instance_lock:
                if not hasattr(JudgeClient, '_instance'):
                    JudgeClient._instance = object.__new__(cls)
        return JudgeClient._instance

    def __init__(self):
        self.authn_token = settings.AUTHN_TOKEN
        self.authz_token = settings.AUTHZ_TOKEN
        if settings.USE_HTTPS:
            self.endpoint = "https://" + settings.JUDGE_HOST
        else:
            self.endpoint = "http://" + settings.JUDGE_HOST + ':' + str(settings.JUDGE_PORT)
        self.session = requests.session()
        self._login()

    def _login(self):
        if self.authn_token:
            self._authenticate()
        if self.authz_token:
            self._authorize()

    def _authenticate(self):
        header = {settings.AUTHN_HEADER: self.authn_token}
        r = requests.post(f"{self.endpoint}/authenticate", headers=header)
        r.raise_for_status()
        self.session.headers.update(header)

    def _authorize(self):
        header = {
            settings.AUTHN_HEADER: self.authn_token,
            settings.AUTHZ_HEADER: self.authz_token
        }
        r = requests.post(f"{self.endpoint}/authorize", headers=header)
        r.raise_for_status()
        self.session.headers.update(header)

    def get_languages(self):
        r = self.session.get(f"{self.endpoint}/languages")
        r.raise_for_status()
        return r.json()
