import os
import logging

logger = logging.getLogger(__name__)


class Logic:
  def __init__(self, config, storage, comm):
    self._config = config
    self._storage = storage  # storage.py
    self._comm = comm  # TODO: communication class: sendEvent

    self._restore()

  def _restore(self):  # TODO
    pass

  def verify_app(self, course_id: int, hash: str) -> str:
    return self._storage.verify_app(course_id, hash)
