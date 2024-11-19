import logging
from .tools import *
from .test_config import *

logger = logging.getLogger()

# event_types
E_INVALID = 0
E_RESOURCES = 1
E_CLASS = 2
E_TEST = 3
E_ASSIGNMENT = 4
event_types = [E_RESOURCES, E_CLASS, E_TEST, E_ASSIGNMENT]
event_types_str = {E_RESOURCES: "resources", E_CLASS: "class", E_TEST: "test", E_ASSIGNMENT: "assignment"}
event_types_to_code = {E_RESOURCES: "e_resources", E_CLASS: "e_class", E_TEST: "e_test", E_ASSIGNMENT: "e_assignment"}
event_types_from_code = {"e_resources": E_RESOURCES, "e_class": E_CLASS, "e_test": E_TEST, "e_assignment": E_ASSIGNMENT}


class Event():
  def __init__(self, id: int, name: str, start_time: datetime.datetime, info: str, published: bool, details: dict = None):
    self.id = id
    self.name = name
    self.type = E_INVALID
    self.start_time = start_time
    self.info: str = info
    self.published: bool = published
    
    if details is not None:
      self.from_dict_details(details)

  def is_not_added(self):
    return self.id == 0

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
      "published": self.published,
      "details": self.to_dict_details(),
    }

    return data


class ResourcesEvent(Event):
  def __init__(self, id: int, name: str, start_time: datetime.datetime, info: str, published: bool, details: dict):
    super().__init__(id, name, start_time, info, published, details)
    self.type = E_RESOURCES

  def from_dict_details(self, details: dict):
    pass

  def to_dict_details(self) -> dict:
    return {}


class ClassEvent(Event):
  def __init__(self, id: int, name: str, start_time: datetime.datetime, info: str, published: bool, details: dict):
    self.duration_m: int = None
    self.url: str = None
    super().__init__(id, name, start_time, info, published, details)
    self.type = E_CLASS

  def from_dict_details(self, details: dict):
    self.duration_m = details["duration_m"]
    self.url = details["url"]

  def to_dict_details(self) -> dict:
    return {
      "duration_m": self.duration_m,
      "url": self.url,
    }


class TestEvent(Event):
  def __init__(self, id: int, name: str, start_time: datetime.datetime, info: str, published: bool, details: dict):
    self.duration_m: int = None
    self.configs: dict[str, TestConfig] = {}
    super().__init__(id, name, start_time, info, published, details)
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
  
  def get_result(self, answers: dict):
    result = 0
    count = 0
    for hash, answer in answers.items():
      config = self.configs.get(hash, None)
      if config is None:
        logger.warning(f"no config found: {hash}")
        continue

      result += self.configs[hash].get_result(answer)
      count += 1

    return int(float(result) / count)
  
  def from_dict_configs(self, configs: dict):
    self.configs: dict[str, TestConfig] = {}
    for config in configs:
      test = get_test_config(config)
      self.configs[test.calc_hash()] = test
  
  def to_dict_configs(self):
    return [config.to_dict() for config in self.configs.values()]


class AssignmentEvent(Event):
  def __init__(self, id: int, name: str, start_time: datetime.datetime, info: str, published: bool, details: dict):
    super().__init__(id, name, start_time, info, published, details)
    self.type = E_ASSIGNMENT

  def from_dict_details(self, details: dict):
    pass

  def to_dict_details(self) -> dict:
    return {}


def get_event(id: int, type: int, name: str, start_time: datetime.datetime, info: str, published: bool = False, details: dict = None):
  if type == E_RESOURCES:
    return ResourcesEvent(id, name, start_time, info, published, details)
  elif type == E_CLASS:
    return ClassEvent(id, name, start_time, info, published, details)
  elif type == E_TEST:
    return TestEvent(id, name, start_time, info, published, details)
  elif type == E_ASSIGNMENT:
    return AssignmentEvent(id, name, start_time, info, published, details)


def get_event_from_dict(data: dict):
  return get_event(data["id"], data["type"], data["name"], datetime_from_str(data["start_time"]), data["info"], data["published"], data.get("details"))
