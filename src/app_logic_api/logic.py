import requests
import logging
from course_classes import *

logger = logging.getLogger()

ep_health = "health"
ep_verify = "verify"
ep_launch_update_users = "app/launch_update_users"

class AppLogic:
  def __init__(self, config):
    self.server_address = config["SERVER_ADDRESS"]
    self.auth_key = config["AUTH_KEY"]
    self.session_key = ""
    self.course = None

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

    self.session_key = r_data["session_key"]
    self.course = Course(data=r_data["course_data"])

    logger.info(f"App verified. Course: {r_data['course_data']}")

    return True

  def start(self):
    r = self.send_req(func=requests.get, path=ep_health)
    if not r.ok:
      raise RuntimeError("can't connect to server")
    
    self.verify()
    
    return True

  def is_first_launch(self):
    return len(self.course.users) == 0

  def is_need_setup(self):
    return len(self.course.events) == 0 or len(self.course.users) == 0

  def is_teacher_user(self, user_id: str):
    return self.course.is_teacher_user(user_id)
  
  def launch_update_users(self):
    users_data = []
    if len(self.course.users):
      for user in self.course.users.values():
        users_data.append(user.to_dict())

    r = self.send_req(func=requests.post, path=ep_launch_update_users, json={"users": users_data})
    if not r.ok:
      raise RuntimeError("can't launch_update_users")
    
    r_data=r.json()
    self.course = Course(data=r_data["course_data"])
