import logging

logger = logging.getLogger(__name__)


class DataStorage():
  def __init__(self, config: dict) -> None:
    if self.validate_config(config):
      self.config = config
      # TODO: do not print because of passwords ???
      logger.info(f"{self.__class__.__name__} config loaded: {config}")
    else:
      raise Exception(f"invalid config: {config}")

  def validate_config(self, config: dict) -> bool:
    pass

  """returns session key to use API and websocket"""
  def verify_app(self, course_id: int, key: str) -> str:
    pass
