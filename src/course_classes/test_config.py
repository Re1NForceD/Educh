import hashlib

# test_types
T_INVALID = 0
T_SINGLE = 1
T_MULTI = 2
T_COMPLIANCE = 3
test_types = [T_SINGLE, T_MULTI]#, T_COMPLIANCE]
test_types_str = {T_SINGLE: "single", T_MULTI: "multi", T_COMPLIANCE: "compliance"}
test_types_to_code = {T_SINGLE: "t_single", T_MULTI: "t_multi", T_COMPLIANCE: "t_compliance"}
test_types_from_code = {"t_single": T_SINGLE, "t_multi": T_MULTI, "t_compliance": T_COMPLIANCE}


class TestConfig:
  def __init__(self, question: str):
    self.type = T_INVALID
    self.question = question
    self.hash: str = ""

  def calc_hash(self) -> str:
    pass

  def to_dict_details(self) -> dict:
    pass

  def to_dict(self):
    return {
      "type": self.type,
      "question": self.question,
      "hash": self.hash,
      "details": self.to_dict_details(),
    }

class TestConfigSignle(TestConfig):
  def __init__(self, question: str, anses: list[str]=None, data: dict=None):
    super().__init__(question)
    self.type = T_SINGLE

    if data is not None:
      self.anses = data.get("anses")
    else:
      if len(anses) < 3:
        raise Exception("incorrect ans lenght")
      self.anses = anses

    self.hash = self.calc_hash()

  def calc_hash(self):
    return hashlib.sha256(f"{self.type}+{self.question}".encode('utf-8')).hexdigest()

  def to_dict_details(self) -> dict:
    return {
      "anses": self.anses,
    }


class TestConfigMulti(TestConfig):
  def __init__(self, question: str, correct: list[str]=None, others: list[str]=None, data: dict=None):
    super().__init__(question)
    self.type = T_MULTI

    if data is not None:
      self.correct = data.get("correct")
      self.others = data.get("others")
    else:
      if len(correct) < 2:
        raise Exception("incorrect correct lenght")
      if len(others) < 2:
        raise Exception("incorrect others lenght")
      self.correct = correct
      self.others = others

    self.hash = self.calc_hash()

  def calc_hash(self):
    return hashlib.sha256(f"{self.type}+{self.question}".encode('utf-8')).hexdigest()

  def to_dict_details(self) -> dict:
    return {
      "correct": self.correct,
      "others": self.others,
    }


# class TestConfigCompliance(TestConfig):
#   def __init__(self, question: str, pairs: list[], data: dict=None):
#     super().__init__(question)
#     self.type = T_COMPLIANCE

#     if data is not None:
#       self.correct = data.get("correct")
#       self.others = data.get("others")
#     else:
#       if len(correct) < 2:
#         raise Exception("incorrect correct lenght")
#       if len(others) < 2:
#         raise Exception("incorrect others lenght")
#       self.correct = correct
#       self.others = others

  #   self.hash = self.calc_hash()

  # def calc_hash(self):
  #   return hashlib.sha256(f"{self.type}+{self.question}.encode('utf-8')").hexdigest()


def get_test_config(data: dict) -> TestConfig:
  type = data["type"]
  if type == T_SINGLE:
    return TestConfigSignle(data["question"], data=data["details"])
  elif type == T_SINGLE:
    return TestConfigMulti(data["question"], data=data["details"])
  # elif type == T_COMPLIANCE:
  #   return TestConfigCompliance(data["question"], data=data["details"])