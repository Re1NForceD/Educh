import datetime

# event_types
E_INVALID = 0
E_GREETINGS = 1
E_RESOURCES = 2
E_CLASS = 3
E_TEST = 4
event_types = [E_GREETINGS, E_RESOURCES, E_CLASS, E_TEST]
event_types_str = {E_GREETINGS: "greetings", E_RESOURCES: "resources", E_CLASS: "class", E_TEST: "test"}
event_types_to_code = {E_GREETINGS: "e_greetings", E_RESOURCES: "e_resources", E_CLASS: "e_class", E_TEST: "e_test"}
event_types_from_code = {"e_greetings": E_GREETINGS, "e_resources": E_RESOURCES, "e_class": E_CLASS, "e_test": E_TEST}

class Event():
  def __init__(self, id: int, start_time: datetime.datetime, duration_m: int):
    self.id = id
    self.type = E_INVALID
    self.start_time = start_time
    self.duration_m = None if duration_m is None or duration_m <= 0 else duration_m

  def to_dict(self) -> dict:
    data = {
      "id": self.id,
      "type": self.type,
      "start_time": None if self.start_time is None else self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
      "duration_m": self.duration_m,
    }

    return data


class GreetingsEvent(Event):
  def __init__(self, id: int, start_time: datetime.datetime, duration_m: int):
    super().__init__(id, start_time, duration_m)
    self.type = E_GREETINGS


class ResourcesEvent(Event):
  def __init__(self, id: int, start_time: datetime.datetime, duration_m: int):
    super().__init__(id, start_time, duration_m)
    self.type = E_RESOURCES


class ClassEvent(Event):
  def __init__(self, id: int, start_time: datetime.datetime, duration_m: int):
    super().__init__(id, start_time, duration_m)
    self.type = E_CLASS


class TestEvent(Event):
  def __init__(self, id: int, start_time: datetime.datetime, duration_m: int):
    super().__init__(id, start_time, duration_m)
    self.type = E_TEST


def get_event(id: int, type: int, start_time: datetime.datetime, duration_m: int):
  if type == E_GREETINGS:
    return GreetingsEvent(id, start_time, duration_m)
  elif type == E_RESOURCES:
    return ResourcesEvent(id, start_time, duration_m)
  elif type == E_CLASS:
    return ClassEvent(id, start_time, duration_m)
  elif type == E_TEST:
    return TestEvent(id, start_time, duration_m)


def get_event_from_dict(data: dict):
  data_start_date = data["start_time"]
  return get_event(data["id"], data["type"], None if data_start_date is None else datetime.datetime.strptime(data_start_date,"%Y-%m-%d %H:%M:%S"), data["duration_m"])
