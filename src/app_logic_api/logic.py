import requests
import logging

logger = logging.getLogger()

ep_health = "health"
ep_verify = "verify"
ep_app_test = "app/test"

class AppLogic:
    def __init__(self, config):
        self.server_address = config["SERVER_ADDRESS"]
        self.auth_key = config["AUTH_KEY"]
        self.session_key = ""

    def get_url(self, path):
        return f"{self.server_address}/{path}"
    
    def send_req(self, func, path, json=None):
        r = func(url=self.get_url(path), json=json, headers={"Session-Key": self.session_key})
        return r

    def verify(self):
        r = self.send_req(func=requests.put, path=ep_verify, json={"auth_key": self.auth_key})
        if not r.ok:
            raise RuntimeError("can't verify app")
        
        r_data = r.json()

        self.course_id = r_data["id"]
        self.course_name = r_data["name"]
        self.session_key = r_data["session_key"]

        logger.info(f"App verified under {self.course_id} - {self.course_name}")

        self.send_req(func=requests.get, path=ep_app_test)

        return True

    def start(self):
        r = self.send_req(func=requests.get, path=ep_health)
        if not r.ok:
            raise RuntimeError("can't connect to server")
        
        self.verify()
        
        return True
