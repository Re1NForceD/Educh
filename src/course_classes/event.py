

# event_types
E_INVALID = 0
E_GREETINGS = 1
E_RESOURCES = 2
E_CLASS = 3
E_TEST = 4


class Event():
  def __init__(self, id, offset_h):
    self.id = id
    self.type = E_INVALID
    self.offset_h = offset_h

  def get_time(self, start_date):
    return start_date + self.offset_h # TODO

  def to_dict(self) -> dict:
    data = {
      "id": self.id,
      "type": self.type,
      "offset_h": self.offset_h,
    }

    return data


class GreetingsEvent(Event):
  def __init__(self, id, offset_h):
    super().__init__(id, offset_h)
    self.type = E_GREETINGS


class ResourcesEvent(Event):
  def __init__(self, id, offset_h):
    super().__init__(id, offset_h)
    self.type = E_RESOURCES


class ClassEvent(Event):
  def __init__(self, id, offset_h):
    super().__init__(id, offset_h)
    self.type = E_CLASS


class TestEvent(Event):
  def __init__(self, id, offset_h):
    super().__init__(id, offset_h)
    self.type = E_TEST


def get_event(id, type, offset_h):
  if type == E_GREETINGS:
    return GreetingsEvent(id, offset_h)
  elif type == E_RESOURCES:
    return ResourcesEvent(id, offset_h)
  elif type == E_CLASS:
    return ClassEvent(id, offset_h)
  elif type == E_TEST:
    return TestEvent(id, offset_h)


def get_event_from_dict(data: dict):
  return get_event(data["id"], data["type"], data["offset_h"])
