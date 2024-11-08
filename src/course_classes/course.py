import logging
import datetime
from .event import *
from .user import *
from .tools import *

logger = logging.getLogger()


class Course:
  def __init__(self, id: int =None, name: str =None, channel_id: str =None, started_at: datetime.datetime =None, data: dict =None):
    if data is not None:
      self.from_dict(data)
    else:
      self.id = id
      self.name = name
      self.channel_id = channel_id
      self.started_at: datetime.datetime = started_at
      self.events: dict[int, Event] = {}
      self.users: dict[str, User] = {}

  def is_can_be_worked_with(self) -> bool:
    if self.channel_id is None:
      return False
    
    for user in self.users.values():
      if user.is_teacher():
        return True
      
    return False
  
  def get_user(self, user_id: str) -> User:
    if user_id in self.users:
      return self.users[user_id]
    return None

  def get_event(self, event_id: int):
    return self.events.get(event_id, None)

  def add_event(self, event: Event):
    self.events[event.id] = event

  def remove_event(self, event_id: int):
    return self.events.pop(event_id, None)

  def is_teacher_user(self, user_id: str):
    return self.users[user_id].is_teacher()

  def is_user_id_exists(self, user_id: str):
    return user_id in self.users

  def add_user(self, user: User) -> bool:
    if self.is_user_id_exists(user.platform_id):
      return False
    
    self.users[user.platform_id] = user
    return True

  def to_dict(self) -> dict:
    data = {
      "id": self.id,
      "name": self.name,
      "channel_id": self.channel_id,
      "started_at": datetime_to_str(self.started_at),
      "events": [],
      "users": [],
    }

    if len(self.events):
      events = []
      for event in self.events.values():
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
    self.channel_id = data["channel_id"]
    self.started_at = datetime_from_str(data["started_at"])

    self.events: dict[int, Event] = {}
    self.users: dict[str, User] = {}

    for event_data in data["events"]:
      self.add_event(get_event_from_dict(event_data))
    
    for user_data in data["users"]:
      self.add_user(User(data=user_data))
