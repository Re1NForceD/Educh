import os
import logging
import base64
import bcrypt

from course_classes import *
from server_storage import *

logger = logging.getLogger(__name__)


class Logic:
  def __init__(self, config, storage, comm):
    self._config = config
    self._storage: DataStorage = storage  # storage.py
    self._comm = comm  # TODO: communication class: sendEvent

    self._restore()

  def _restore(self): # TODO
    pass

  def verify_app(self, auth_key: str) -> int:
    # mock_key = base64.b64encode("1+dGVzdF9jb3Vyc2U=".encode('utf-8'), altchars=b"()")
    course_id_str, course_key = base64.b64decode(auth_key, altchars=b"()").decode('utf-8').split("+")
    course_id = int(course_id_str)
    
    course_key_db = self._storage.get_course_auth_data(course_id)

    if not bcrypt.checkpw(course_key.encode('utf-8'), course_key_db.encode('utf-8')):
      logger.error(f"invalid course creds: {course_id}, {course_key}")
      return None

    logger.info(f"app for course <{course_id}> is verified")
    
    return course_id

  def get_course_data(self, course_id: int):
    return self._storage.get_course_data(course_id)

  def update_users(self, course: Course, users: list[User]):
    self._storage.update_users(course, users)

  def update_essensials(self, course_id: int, channel_id: str=None, started_at: datetime.datetime=None):
    self._storage.update_essensials(course_id, channel_id, started_at)

  def set_events_published(self, course_id: int, event_ids: list[int]):
    self._storage.set_events_published(course_id, event_ids)

  def add_events(self, course_id: int, events: list[Event]):
    self._storage.add_events(course_id, events)

  def update_events(self, course_id: int, events: list[Event]):
    self._storage.update_events(course_id, events)

  def remove_events(self, course_id: int, events: list[Event]):
    self._storage.remove_events(course_id, events)

  def get_event_submissions(self, course_id: int):
    return self._storage.get_event_submissions(course_id)

  def post_event_submission(self, course: Course, event_id: int, user_id: str, submission: dict, submitter_id, result):
    if result is None:
      result = course.grade_submission(event_id, submission)
    id = self._storage.save_event_submission(course.id, event_id, user_id, submission, submitter_id, result)
    return [id, result]
  
  def grade_event_submission(self, submission_id, submitter_id, result) -> bool:
    return self._storage.grade_event_submission(submission_id, submitter_id, result)
