import logging
from course_classes import *

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
  
  def create_course(self, name, hash) -> int:
    pass
  
  def get_course_auth_data(self, course_id: int) -> str:
    pass
  
  def get_course_data(self, course_id: int) -> Course:
    pass

  def update_users(self, course: Course, users: list[User]) -> None:
    pass

  def update_essensials(self, course_id: int, channel_id: str=None, started_at: datetime.datetime=None):
    pass
  
  def set_events_published(self, course_id: int, event_ids: list[int]):
    pass

  def add_events(self, course_id: int, events: list[Event]):
    pass

  def update_events(self, course_id: int, events: list[Event]):
    pass

  def remove_events(self, course_id: int, events: list[Event]):
    pass
  
  def get_event_submissions(self, course_id: int):
    pass
  
  def save_event_submission(self, course_id: int, event_id: int, user_id: str, submission: dict, submitter_id, result):
    pass
  
  def grade_event_submission(self, submission_id, submitter_id, result) -> bool:
    pass
