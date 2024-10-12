import logging
import datetime
from .event import *

logger = logging.getLogger()


class Course:
  def __init__(self, id=None, name=None, start_date=None, data=None):
    if data is not None:
      self.from_dict(data)
    else:
      self.id = id
      self.name = name
      self.start_date = start_date
      self.events = []

  def to_dict(self) -> dict:
    data = {
      "id": self.id,
      "name": self.id,
      "start_date": self.start_date.strftime("%d/%m/%Y"),
      "events": []
    }

    if len(self.events):
      events = []
      for event in self.events:
        events.append(event.to_dict())
      data["events"] = events

    return data
  
  def from_dict(self, data: dict):
    self.id = data["id"]
    self.name = data["name"]
    self.start_date = datetime.datetime.strptime(data["start_date"],"%d/%m/%Y").date()
    self.events = []
    for event_data in data["events"]:
      self.events.append(get_event_from_dict(event_data))

  def set_start_date(self, start_date):
    self.start_date = start_date

  def add_event(self, event: Event):
    self.events.append(event)
