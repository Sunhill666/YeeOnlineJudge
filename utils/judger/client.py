import requests
from django.conf import settings


class Client:
    authn_token = None
    authz_token = None
    endpoint = None
    session = None

    def __init__(self):
        self.authn_token = settings.AUTHN_TOKEN
        self.authz_token = settings.AUTHZ_TOKEN
        if settings.USE_HTTPS:
            self.endpoint = "https://" + settings.JUDGE_HOST + ':' + str(settings.JUDGE_PORT)
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
