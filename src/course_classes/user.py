U_GUEST = 1
U_LEARNER = 2
U_TEACHER = 3
U_MASTER = 4

class User:
  def __init__(self, platform_id: str = None, name: str = None, role: int = None, data: dict = None):
    if data is not None:
      self.from_dict(data)
    else:
      self.platform_id = platform_id
      self.name = name
      self.role = role

  def to_dict(self) -> dict:
    data = {
      "platform_id": self.platform_id,
      "name": self.name,
      "role": self.role,
    }

    return data
  
  def from_dict(self, data: dict):
    self.platform_id = data["platform_id"]
    self.name = data["name"]
    self.role = data["role"]
