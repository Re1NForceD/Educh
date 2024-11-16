U_GUEST = 1
U_LEARNER = 2
U_TEACHER = 3
U_MASTER = 4
user_roles = [U_GUEST, U_LEARNER, U_TEACHER, U_MASTER]
user_roles_str = {U_GUEST: "guest", U_LEARNER: "learner", U_TEACHER: "teacher", U_MASTER: "master"}
user_roles_to_code = {U_GUEST: "u_guest", U_LEARNER: "u_learner", U_TEACHER: "u_teacher", U_MASTER: "u_master"}
user_roles_from_code = {"u_guest": U_GUEST, "u_learner": U_LEARNER, "u_teacher": U_TEACHER, "u_master": U_MASTER}

class User:
  def __init__(self, platform_id: str = None, name: str = None, role: int = None, data: dict = None):
    if data is not None:
      self.from_dict(data)
    else:
      self.platform_id = platform_id
      self.name = name
      self.role = role

  def is_learner(self):
    return self.role in [U_LEARNER]

  def is_teacher(self):
    return self.role in [U_TEACHER, U_MASTER]

  def is_guest(self):
    return self.role in [U_GUEST]

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
