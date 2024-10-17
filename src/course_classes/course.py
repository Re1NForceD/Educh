import logging
import datetime
from .event import *
from .user import *

logger = logging.getLogger()


class Course:
  def __init__(self, id: int =None, name: str =None, start_date: datetime.datetime =None, data: dict =None):
    if data is not None:
      self.from_dict(data)
    else:
      self.id = id
      self.name = name
      self.start_date: datetime.datetime = start_date
      self.events: list[Event] = []
      self.users: dict[str, User] = {}

  def set_start_date(self, start_date):
    self.start_date = start_date

  def add_event(self, event: Event):
    self.events.append(event)

  def is_teacher_user(self, user_id: str):
    return self.users[user_id].is_teacher()

  def is_user_exists(self, user: User):
    return user.platform_id in self.users

  def add_user(self, user: User):
    if self.is_user_exists(user):
      return
    
    self.users[user.platform_id] = user

  def to_dict(self) -> dict:
    data = {
      "id": self.id,
      "name": self.name,
      "start_date": None if self.start_date is None else self.start_date.strftime("%Y-%m-%d %H:%M:%S"),
      "events": [],
      "users": [],
    }

    if len(self.events):
      events = []
      for event in self.events:
        events.append(event.to_dict())
      data["events"] = events

    if len(self.users):
      users = []
      for user in self.users.values():
        users.append(user.to_dict())
      data["users"] = users

    return data
  
  def from_dict(self, data: dict):
    self.id = data["id"]
    self.name = data["name"]

    data_start_date = data["start_date"]
    self.start_date = None if data_start_date is None else datetime.datetime.strptime(data_start_date,"%Y-%m-%d %H:%M:%S")

    self.events: list[Event] = []
    self.users: dict[str, User] = {}

    for event_data in data["events"]:
      self.events.append(get_event_from_dict(event_data))
    
    for user_data in data["users"]:
      self.add_user(User(data=user_data))
