import os
import logging

from course_classes import *
from server_storage import *

logger = logging.getLogger(__name__)


class Logic:
  def __init__(self, config, storage, comm):
    self._config = config
    self._storage: DataStorage = storage  # storage.py
    self._comm = comm  # TODO: communication class: sendEvent

    self._restore()

  def _restore(self):  # TODO
    pass

  def verify_app(self, course_id: int, hash: str) -> str:
    return self._storage.verify_app(course_id, hash)

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

  def get_event_submitions(self, course_id: int):
    return self._storage.get_event_submitions(course_id)

  def post_event_submition(self, course: Course, event_id: int, user_id: str, submition: dict, result):
    if result is None:
      result = course.grade_submition(event_id, submition)
    self._storage.save_event_submition(course.id, event_id, user_id, submition, result)
    return result
