import requests
import logging
from course_classes import *

logger = logging.getLogger()

ep_health = "health"
ep_verify = "verify"
ep_update_users = "app/update_users"
ep_update_essensials = "app/update_essensials"
ep_update_events = "app/update_events"
ep_remove_events = "app/remove_events"
ep_set_events_published = "app/set_events_published"
ep_put_event_submition = "app/put_event_submition"

class AppLogic:
  def __init__(self, config):
    self.server_address = config["SERVER_ADDRESS"]
    self.__auth_key = config["AUTH_KEY"]
    self.__session_key = ""
    self.course = None

  def get_url(self, path):
    return f"{self.server_address}/{path}"
  
  def send_req(self, func, path, json=None):
    r = func(url=self.get_url(path), json=json, headers={"Session-Key": self.__session_key})
    return r

  def verify(self):
    r = self.send_req(func=requests.put, path=ep_verify, json={"auth_key": self.__auth_key})
    if not r.ok:
      raise RuntimeError("can't verify app")
    
    r_data = r.json()

    self.__session_key = r_data["session_key"]
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
    return self.course.channel_id is None or len(self.course.users) == 0

  def is_can_start_course(self):
    return len(self.course.events) > 0

  def is_teacher_user(self, user_id: str):
    return self.course.is_teacher_user(user_id)

  def is_in_process(self):
    return self.course.started_at is not None
  
  def update_users(self):
    users_data = []
    if len(self.course.users):
      for user in self.course.users.values():
        users_data.append(user.to_dict())

    r = self.send_req(func=requests.post, path=ep_update_users, json={"users": users_data})
    if not r.ok:
      raise RuntimeError("can't update_users")
    
    r_data=r.json()
    self.course = Course(data=r_data["course_data"])
  
  def update_essensials(self, channel_id: str=None, started_at: datetime.datetime=None):
    r = self.send_req(func=requests.put, path=ep_update_essensials, json={"channel_id":channel_id,"started_at": datetime_to_str(started_at)})
    if not r.ok:
      raise RuntimeError("can't update_essensials")
    
    if channel_id is not None:
      self.course.channel_id = channel_id

    if started_at is not None:
      self.course.started_at = started_at

  def set_events_published(self, events: list[Event]):
    r = self.send_req(func=requests.put, path=ep_set_events_published, json={"event_ids":[event.id for event in events]})
    if not r.ok:
      raise RuntimeError("can't set_events_published")
    
    for event in events:
      self.course.events[event.id].published = True # TODO: set datetime
  
  def update_events(self, events: list[Event]):
    r = self.send_req(func=requests.put, path=ep_update_events, json={"events": [event.to_dict() for event in events]})
    if not r.ok:
      raise RuntimeError("can't update_events")
    
    r_data=r.json()
    self.course = Course(data=r_data["course_data"])
  
  def remove_events(self, events: list[Event]):
    r = self.send_req(func=requests.delete, path=ep_remove_events, json={"events": [event.to_dict() for event in events]})
    if not r.ok:
      raise RuntimeError("can't remove_events")
    
    r_data=r.json()
    self.course = Course(data=r_data["course_data"])

  def start_course(self) -> bool:
    if self.course.started_at is not None:
      logger.warning(f"try to start course, but it already started")
      return False
    
    start_time = datetime.datetime.now()
    self.update_essensials(started_at=start_time)
    return True
  
  def submit_test_answers(self, event_id: int, user_id: str, answers: dict[str, list[str]]):
    logger.debug(f"submit_test_answers {user_id} - {event_id} - {answers}")
    event: Event = self.course.get_event(event_id)
    
    if event is None:
      logger.error(f"cant find event: {event_id}")
      return
    
    r = self.send_req(func=requests.post, path=ep_put_event_submition, json={"event_id": event_id, "user_id": user_id, "answers": answers})
    if not r.ok:
      raise RuntimeError("can't put_event_submition")
    
    r_data=r.json()
    self.course.colect_tests_results({event_id: {user_id: {"answers": answers, "result": r_data["result"]}}})
    
  def user_submit_assignment(self, event: AssignmentEvent, user_id: str, files):
    # TODO: save submition on api
    pass
