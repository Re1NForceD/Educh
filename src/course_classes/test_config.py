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

  def validate():
    return "invalid class"

  def calc_hash(self) -> str:
    pass

  def get_result(self, answer: dict):
    pass

  def to_dict_details(self) -> dict:
    pass

  def to_dict(self):
    return {
      "type": self.type,
      "question": self.question,
      "details": self.to_dict_details(),
    }


class TestConfigSignle(TestConfig):
  def __init__(self, question: str, variants: list[str]=None, data: dict=None):
    self.variants: dict[str, str] = {}
    self.ans_hash: str = ""
    super().__init__(question)
    self.type = T_SINGLE

    if data is not None:
      self.variants = data.get("variants", {})
      self.ans_hash = data.get("ans", "")
    else:
      self.set_variants(variants)

  def set_variants(self, variants: list[str]):
    self.variants: dict[str, str] = {}
    self.ans_hash: str = ""

    if len(variants) == 0:
      return
    
    for var in variants:
      self.variants[hashlib.md5(var.encode('utf-8')).hexdigest()] = var
    self.ans_hash = hashlib.md5(variants[0].encode('utf-8')).hexdigest()

  def add_variant(self, variant: str):
    var_hash = hashlib.md5(variant.encode('utf-8')).hexdigest()
    if len(self.variants) == 0:
      self.ans_hash = var_hash
    
    self.variants[var_hash] = variant

  def remove_variant(self, var_hash: str):
    poped = self.variants.pop(var_hash, None)
    if poped is None:
      return
    
    if self.ans_hash == var_hash:
      for hash in self.variants:
        self.ans_hash = hash
        continue

  def get_result(self, answer: dict):
    return 100 if self.ans_hash == answer["var_hash"] else 0

  def validate(self):
    return "need 3 variants" if len(self.variants) < 3 else None

  def calc_hash(self):
    return hashlib.md5(f"{self.type}+{self.question}".encode('utf-8')).hexdigest()

  def to_dict_details(self) -> dict:
    return {
      "ans": self.ans_hash,
      "variants": self.variants,
    }


class TestConfigMulti(TestConfig):
  def __init__(self, question: str, correct: list[str]=None, incorrect: list[str]=None, data: dict=None):
    self.correct: dict[str, str] = {}
    self.incorrect: dict[str, str] = {}
    super().__init__(question)
    self.type = T_MULTI

    if data is not None:
      self.correct = data.get("correct", {})
      self.incorrect = data.get("incorrect", {})
    else:
      for cor in correct:
        self.add_correct(cor)
      for incor in incorrect:
        self.add_incorrect(incor)

  def add_correct(self, variant: str):
    var_hash = hashlib.md5(variant.encode('utf-8')).hexdigest()
    self.remove_variant(var_hash)
    self.correct[var_hash] = variant

  def add_incorrect(self, variant: str):
    var_hash = hashlib.md5(variant.encode('utf-8')).hexdigest()
    self.remove_variant(var_hash)
    self.incorrect[var_hash] = variant

  def remove_variant(self, var_hash: str):
    self.correct.pop(var_hash, None)
    self.incorrect.pop(var_hash, None)

  def get_result(self, answer: dict):
    result = 0
    for var in answer["vars_hash"]:
      if var in self.incorrect:
        return 0
      if var in self.correct:
        result += 100
    return int(float(result) / len(self.correct))

  def validate(self):
    return "need atleast 2 correct variants" if len(self.correct) < 2 else "need atleast 3 incorrect variants" if len(self.incorrect) < 3 else None

  def calc_hash(self):
    return hashlib.md5(f"{self.type}+{self.question}".encode('utf-8')).hexdigest()

  def to_dict_details(self) -> dict:
    return {
      "correct": self.correct,
      "incorrect": self.incorrect,
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

  # def calc_hash(self):
  #   return hashlib.md5(f"{self.type}+{self.question}.encode('utf-8')").hexdigest()


def init_test_config(type: int):
  if type == T_SINGLE:
    return TestConfigSignle("", [])
  elif type == T_MULTI:
    return TestConfigMulti("", [], [])

def get_test_config(data: dict) -> TestConfig:
  type = data["type"]
  if type == T_SINGLE:
    return TestConfigSignle(data["question"], data=data["details"])
  elif type == T_MULTI:
    return TestConfigMulti(data["question"], data=data["details"])
  # elif type == T_COMPLIANCE:
  #   return TestConfigCompliance(data["question"], data=data["details"])
