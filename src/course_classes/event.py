from .tools import *

# event_types
E_INVALID = 0
E_RESOURCES = 1
E_CLASS = 2
E_TEST = 3
event_types = [E_RESOURCES, E_CLASS, E_TEST]
event_types_str = {E_RESOURCES: "resources", E_CLASS: "class", E_TEST: "test"}
event_types_to_code = {E_RESOURCES: "e_resources", E_CLASS: "e_class", E_TEST: "e_test"}
event_types_from_code = {"e_resources": E_RESOURCES, "e_class": E_CLASS, "e_test": E_TEST}

class Event():
  def __init__(self, id: int, name: str, start_time: datetime.datetime, duration_m: int):
    self.id = id
    self.name = name
    self.type = E_INVALID
    self.start_time = start_time
    self.duration_m = None if duration_m is None or duration_m <= 0 else duration_m

  def to_dict(self) -> dict:
    data = {
      "id": self.id,
      "name": self.name,
      "type": self.type,
      "start_time": datetime_to_str(self.start_time),
      "duration_m": self.duration_m,
    }

    return data


class ResourcesEvent(Event):
  def __init__(self, id: int, name: str, start_time: datetime.datetime, duration_m: int):
    super().__init__(id, name, start_time, duration_m)
    self.type = E_RESOURCES


class ClassEvent(Event):
  def __init__(self, id: int, name: str, start_time: datetime.datetime, duration_m: int):
    super().__init__(id, name, start_time, duration_m)
    self.type = E_CLASS


class TestEvent(Event):
  def __init__(self, id: int, name: str, start_time: datetime.datetime, duration_m: int):
    super().__init__(id, name, start_time, duration_m)
    self.type = E_TEST


def get_event(id: int, name: str, type: int, start_time: datetime.datetime, duration_m: int):
  if type == E_RESOURCES:
    return ResourcesEvent(id, name, start_time, duration_m)
  elif type == E_CLASS:
    return ClassEvent(id, name, start_time, duration_m)
  elif type == E_TEST:
    return TestEvent(id, name, start_time, duration_m)


def get_event_from_dict(data: dict):
  return get_event(data["id"], data["name"], data["type"], datetime_from_str(data["start_time"]), data["duration_m"])
