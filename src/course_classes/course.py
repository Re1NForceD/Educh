import logging
import datetime
from .event import *
from .user import *
from .tools import *

logger = logging.getLogger()


class Course:
  def __init__(self, id: int =None, name: str =None, channel_id: str =None, started_at: datetime.datetime =None, data: dict =None):
    if data is not None:
      self.from_dict(data)
    else:
      if id is None or name is None:
        raise RuntimeError("need id and name or data to create course")
      
      self.id = id
      self.name = name
      self.channel_id = channel_id
      self.started_at: datetime.datetime = started_at
      self.events: dict[int, Event] = {}
      self.users: dict[str, User] = {}

    self.submissions: dict[int, dict[str, dict]] = {}
    self.submissions_by_id: dict[int, list[int, str, dict]] = {}

  def is_can_be_worked_with(self) -> bool:
    if self.channel_id is None:
      return False
    
    for user in self.users.values():
      if user.is_teacher():
        return True
      
    return False
  
  def get_user(self, user_id: str) -> User:
    if user_id in self.users:
      return self.users[user_id]
    return None
  
  def get_next_event(self):
    next_event: Event = None
    for event in self.events.values():
      if event.published:
        continue
      elif next_event is None or next_event.start_time > event.start_time:
        next_event = event
    return next_event

  def get_event(self, event_id: int):
    return self.events.get(event_id, None)

  def add_event(self, event: Event):
    self.events[event.id] = event

  def remove_event(self, event_id: int):
    return self.events.pop(event_id, None)

  def is_user_id_exists(self, user_id: str):
    return user_id in self.users

  def add_user(self, user: User) -> bool:
    if self.is_user_id_exists(user.platform_id):
      return False
    
    self.users[user.platform_id] = user
    return True

  def to_dict(self) -> dict:
    data = {
      "id": self.id,
      "name": self.name,
      "channel_id": self.channel_id,
      "started_at": datetime_to_str(self.started_at),
      "events": [],
      "users": [],
    }

    if len(self.events):
      events = []
      for event in self.events.values():
        events.append(event.to_dict())
      data["events"] = events

    if len(self.users):
      users = []
      for user in self.users.values():
        users.append(user.to_dict())
      data["users"] = users

    return data
  
  def from_dict(self, data: dict):
    self.id = data["id"]
    self.name = data["name"]

    if self.id is None or self.name is None:
      raise RuntimeError("course_data has no id or name")
    
    self.channel_id = data["channel_id"]
    self.started_at = datetime_from_str(data["started_at"])

    self.events: dict[int, Event] = {}
    self.users: dict[str, User] = {}

    for event_data in data["events"]:
      self.add_event(get_event_from_dict(event_data))
    
    for user_data in data["users"]:
      self.add_user(User(data=user_data))

  def get_all_ungraded_submissions(self):
    ungraded = 0
    for submission in self.submissions_by_id.values():
      if submission[2]["result"] is None:
        ungraded += 1
    return ungraded

  def colect_submission(self, event_submissions: dict): # {submission_id: [event_id, user_id, submission}}
    for submission_id, submission_data in event_submissions.items():
      if not isinstance(submission_id, int):
        submission_id = int(submission_id)

      event_id = submission_data[0]
      user_id = submission_data[1]
      submission = submission_data[2]
      event: Event = self.get_event(event_id)
      if event is None:
        logger.warning(f"try to collect submissions but event not found: {event_id}")
        continue
      
      event_submissions: dict = self.submissions.get(event_id, None)
      if event_submissions is None:
        self.submissions[event_id] = {}
        event_submissions = self.submissions.get(event_id, None)
      
      # for user_id, submission in submissions.items():
      user: User = self.get_user(user_id)
      if user is None: # or user != U_LEARNER:
        logger.warning(f"try to submission for invalid user: {user} - {user.role if user is not None else E_INVALID}")
        continue
      
      if user_id in event_submissions:
        logger.warning(f"update user {user_id} event submission")

      event_submissions[user_id] = submission
      self.submissions_by_id[submission_id] = submission_data

      if submission.get("date", None) is None:
        submission["date"] = datetime_to_str(datetime.datetime.now())

  def update_submission(self, submitter_id, submission_id, result):
    submission = self.submissions_by_id[submission_id][2]
    submission["submitter_id"] = submitter_id
    submission["result"] = result

  def grade_submission(self, event_id, submission):
    event: Event = self.get_event(event_id)

    if event is None:
      logger.error(f"no event found: {event_id}")
      return None

    if event.type == E_TEST:
      return event.get_result(submission)
    
    return None
