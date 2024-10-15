import logging
import datetime
from .event import *
from .user import *

logger = logging.getLogger()


class Course:
  def __init__(self, id=None, name=None, start_date=None, data=None):
    if data is not None:
      self.from_dict(data)
    else:
      self.id = id
      self.name = name
      self.start_date = start_date
      self.events: list[Event] = []
      self.learners: list[User] = []
      self.teachers: list[User] = []

  def set_start_date(self, start_date):
    self.start_date = start_date

  def add_event(self, event: Event):
    self.events.append(event)

  def is_user_exists(self, user: User):
    for learner in self.learners:
      if learner.platform_id == user.platform_id:
        return True
    
    for teacher in self.teachers:
      if teacher.platform_id == user.platform_id:
        return True
    
    return False

  def add_user(self, user: User):
    if self.is_user_exists(user):
      return
    
    if user.role == U_LEARNER:
      self.learners.append(user)
    elif user.role in [U_TEACHER, U_MASTER]:
      self.teachers.append(user)

  def to_dict(self) -> dict:
    data = {
      "id": self.id,
      "name": self.name,
      "start_date": self.start_date.strftime("%d/%m/%Y"),
      "events": [],
      "learners": [],
      "teachers": [],
    }

    if len(self.events):
      events = []
      for event in self.events:
        events.append(event.to_dict())
      data["events"] = events

    if len(self.learners):
      learners = []
      for learner in self.learners:
        learners.append(learner.to_dict())
      data["learners"] = learners

    if len(self.teachers):
      teachers = []
      for teacher in self.teachers:
        teachers.append(teacher.to_dict())
      data["teachers"] = teachers

    return data
  
  def from_dict(self, data: dict):
    self.id = data["id"]
    self.name = data["name"]
    self.start_date = datetime.datetime.strptime(data["start_date"],"%d/%m/%Y").date()
    self.events: list[Event] = []
    self.learners: list[User] = []
    self.teachers: list[User] = []

    for event_data in data["events"]:
      self.events.append(get_event_from_dict(event_data))
    
    for learner_data in data["learners"]:
      self.add_user(User(data=learner_data))
    
    for teacher_data in data["teachers"]:
      self.add_user(User(data=teacher_data))
