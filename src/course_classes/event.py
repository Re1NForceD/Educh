from .tools import *
from .test_config import *

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
  def __init__(self, id: int, name: str, start_time: datetime.datetime, info: str, details: dict = None):
    self.id = id
    self.name = name
    self.type = E_INVALID
    self.start_time = start_time
    self.info: str = info
    
    if details is not None:
      self.from_dict_details(details)

  def from_dict_details(self, details: dict):
    pass

  def to_dict_details(self) -> dict:
    pass

  def to_dict(self) -> dict:
    data = {
      "id": self.id,
      "name": self.name,
      "type": self.type,
      "start_time": datetime_to_str(self.start_time),
      "info": self.info,
      "details": self.to_dict_details(),
    }

    return data


class ResourcesEvent(Event):
  def __init__(self, id: int, name: str, start_time: datetime.datetime, info: str, details: dict):
    super().__init__(id, name, start_time, info, details)
    self.type = E_RESOURCES

  def from_dict_details(self, details: dict):
    pass

  def to_dict_details(self) -> dict:
    return {}


class ClassEvent(Event):
  def __init__(self, id: int, name: str, start_time: datetime.datetime, info: str, details: dict):
    self.duration_m: int = None
    super().__init__(id, name, start_time, info, details)
    self.type = E_CLASS

  def from_dict_details(self, details: dict):
    self.duration_m = details["duration_m"]

  def to_dict_details(self) -> dict:
    return {
      "duration_m": self.duration_m,
    }


class TestEvent(Event):
  def __init__(self, id: int, name: str, start_time: datetime.datetime, info: str, details: dict):
    self.duration_m: int = None
    self.configs: dict[str, TestConfig] = {}
    super().__init__(id, name, start_time, info, details)
    self.type = E_TEST

  def from_dict_details(self, details: dict):
    self.duration_m = details["duration_m"]
    self.from_dict_configs(details["configs"])

  def to_dict_details(self) -> dict:
    return {
      "duration_m": self.duration_m,
      "configs": self.to_dict_configs(),
    }
  
  def add_config(self, test: TestConfig):
    self.configs[test.calc_hash()] = test
  
  def remove_config(self, test_hash: str):
    return self.configs.pop(test_hash)
  
  def from_dict_configs(self, configs: dict):
    self.configs: dict[str, TestConfig] = {}
    for config in configs:
      test = get_test_config(config)
      self.configs[test.calc_hash()] = test
  
  def to_dict_configs(self):
    return [config.to_dict() for config in self.configs.values()]


def get_event(id: int, type: int, name: str, start_time: datetime.datetime, info: str, details: dict = None):
  if type == E_RESOURCES:
    return ResourcesEvent(id, name, start_time, info, details)
  elif type == E_CLASS:
    return ClassEvent(id, name, start_time, info, details)
  elif type == E_TEST:
    return TestEvent(id, name, start_time, info, details)


def get_event_from_dict(data: dict):
  return get_event(data["id"], data["type"], data["name"], datetime_from_str(data["start_time"]), data["info"], data.get("details"))
