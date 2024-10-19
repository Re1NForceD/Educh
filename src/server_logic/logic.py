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

  def update_users(self, course_id: int, users: list[User]):
    self._storage.update_users(course_id, users)

  def update_essensials(self, course_id: int, channel_id: str=None, start_date: datetime.datetime=None):
    self._storage.update_essensials(course_id, channel_id, start_date)
