import os
import bcrypt
import logging
import mysql.connector
import json
from mysql.connector import Error

from .storage import *

logger = logging.getLogger(__name__)


class MySQLStorage(DataStorage):
  def __init__(self, config: dict) -> None:
    super().__init__(config)

    self.__db_host = self.config["db_host"]
    self.__db_port = self.config["db_port"]
    self.__db_name = self.config["db_name"]
    self.__db_user = self.config["db_user"]
    self.__db_password = self.config["db_password"]

    self.get_cnx().close()

    logger.info("MySQLStorage initialized successfuly")

  def validate_config(self, config: dict) -> bool:
    props = ["db_host", "db_port", "db_name", "db_user", "db_password"]  # TODO
    return all(prop in config for prop in props)

  def get_cnx(self):
    try:
      cnx = mysql.connector.connect(
          host=self.__db_host,
          port=self.__db_port,
          database=self.__db_name,
          user=self.__db_user,
          password=self.__db_password,
      )

      if not cnx.is_connected():
        raise Error("Not connected to db")

      return cnx
    except Error as e:
      raise ConnectionError(f"Error connecting to the database: {e}")

  def exec_select(self, cnx, query: str):
    with cnx.cursor() as cursor:
      cursor.execute(query)
      return cursor.fetchall()

  def exec_insert(self, cnx, query: str):
    with cnx.cursor() as cursor:
      cursor.execute(query)
      return cursor.lastrowid

  def exec_update(self, cnx, query: str):
    with cnx.cursor() as cursor:
      cursor.execute(query)
      return cursor.rowcount

  def verify_app(self, course_id: int, key: str) -> str:
    cnx = self.get_cnx()
    rows = self.exec_select(
        cnx, f"select id, name, hash from course where id = {course_id}")

    if len(rows) != 1:
      logger.error(f"course {course_id} has invalid record")
      return ""

    if not bcrypt.checkpw(key.encode('utf-8'), rows[0][2].encode('utf-8')):
      logger.error(f"invalid course creds: {course_id}, {key}")
      return ""

    return rows[0][1]
  
  def get_event(self, db_row) -> Event:
    event = get_event(id=db_row[0], type=db_row[1], name=db_row[2], start_time=db_row[3], info=db_row[4], published=db_row[5])
    if event.type == E_RESOURCES: # cols: none
      pass
    elif event.type == E_CLASS: # cols: 6
      event.duration_m = db_row[6]
    elif event.type == E_TEST: # cols: 7, 8
      event.duration_m = db_row[7]
      event.from_dict_configs(json.loads(db_row[8]))
    elif event.type == E_ASSIGNMENT: # cols: none
      pass
    return event
  
  def get_course_data(self, course_id: int) -> Course:
    cnx = self.get_cnx()
    
    general_info = self.exec_select(
        cnx, f"select id, name, channel_id, started_at from course where id = {course_id}")
    
    if len(general_info) != 1:
      raise RuntimeError(f"invalid course info in db for: {course_id}")
    
    course = Course(id=general_info[0][0], name=general_info[0][1], channel_id=general_info[0][2], started_at=general_info[0][3])
    
    events = self.exec_select(
        cnx, f"select ce.id, ce.event_type_id, ce.name, ce.start_time, ce.info, ce.published, cedc.duration_m, cedt.duration_m, cedt.configs from course_event ce left outer join course_event_details_resources cerd on ce.id = cerd.event_id left outer join course_event_details_class cedc on ce.id = cedc.event_id left outer join course_event_details_test cedt on ce.id = cedt.event_id left outer join course_event_details_assignment cera on ce.id = cera.event_id where ce.course_id = {course_id} order by ce.start_time")
    if len(events):
      for event_data in events:
        course.add_event(self.get_event(event_data))
    
    users = self.exec_select(
        cnx, f"select cu.platform_id, cu.name, cu.role_id from course_user cu where cu.course_id = {course_id}")
    if len(users):
      for user_data in users:
        course.add_user(User(*user_data))

    return course
  
  def update_users(self, course: Course, users: list[User]) -> None:
    cnx = self.get_cnx()
    for user in users:
      if course.get_user(user.platform_id) is None:
        self.exec_insert(cnx, f"insert into course_user (course_id, platform_id, name, role_id) values({course.id}, '{user.platform_id}', '{user.name}', {user.role})")
      else:
        self.exec_update(cnx, f"update course_user set name='{user.name}', role_id={user.role} where course_id={course.id} and platform_id='{user.platform_id}'")
    cnx.commit()

  def update_essensials(self, course_id: int, channel_id: str=None, started_at: datetime.datetime=None):
    values_update = []

    if channel_id is not None:
      values_update.append(f"channel_id='{channel_id}'")
    
    if started_at is not None:
      values_update.append(f"started_at='{datetime_to_str(started_at)}'")
    
    if len(values_update) == 0:
      return
    
    cnx = self.get_cnx()
    self.exec_update(cnx, f"update course set {','.join(values_update)} where id = {course_id}")
    cnx.commit()

  def set_events_published(self, course_id: int, event_ids: list[int]):
    cnx = self.get_cnx()
    self.exec_update(cnx, f"update course_event set published = 1 where course_id = {course_id} and id in ({','.join(map(str, event_ids))})")
    cnx.commit()

  def insert_event_details_resources(self, cnx, event: ResourcesEvent):
    self.exec_insert(cnx, f"insert into course_event_details_resources (event_id) values({event.id})")

  def insert_event_details_class(self, cnx, event: ClassEvent):
    self.exec_insert(cnx, f"insert into course_event_details_class (event_id, duration_m) values({event.id}, {event.duration_m})")

  def insert_event_details_test(self, cnx, event: TestEvent):
    self.exec_insert(cnx, f"insert into course_event_details_test (event_id, duration_m, configs) values({event.id}, {event.duration_m}, '{json.dumps(event.to_dict_configs())}')")

  def insert_event_details_assignment(self, cnx, event: AssignmentEvent):
    self.exec_insert(cnx, f"insert into course_event_details_assignment (event_id) values({event.id})")

  def insert_event_details(self, cnx, event: Event):
    if event.type == E_RESOURCES:
      self.insert_event_details_resources(cnx, event)
    elif event.type == E_CLASS:
      self.insert_event_details_class(cnx, event)
    elif event.type == E_TEST:
      self.insert_event_details_test(cnx, event)
    elif event.type == E_ASSIGNMENT:
      self.insert_event_details_assignment(cnx, event)

  def insert_event(self, cnx, course_id: int, event: Event):
    event_id = self.exec_insert(cnx, f"insert into course_event (course_id, event_type_id, name, start_time, info) values({course_id}, {event.type}, '{event.name}', '{datetime_to_str(event.start_time)}', {repr(event.info)})")
    event.id = event_id
    self.insert_event_details(cnx, event)

  def add_events(self, course_id: int, events: list[Event]):
    cnx = self.get_cnx()
    for event in events:
      self.insert_event(cnx, course_id, event)
    cnx.commit()

  def update_event_base(self, cnx, course_id: int, event: Event):
    updated_rows = self.exec_update(cnx, f"update course_event set name='{event.name}', start_time='{datetime_to_str(event.start_time)}', info={repr(event.info)}, published={event.published} where course_id={course_id} and id={event.id} and event_type_id={event.type}")
    if updated_rows != 1:
      logger.error(f"incorrect event update, updated rows: {updated_rows}, for event: {event.to_dict()}")

  def update_event_details_resources(self, cnx, event: ResourcesEvent):
    pass
    # self.exec_update(cnx, f"update course_event_details_resources set info='{event.info}' where event_id={event.id}")

  def update_event_details_class(self, cnx, event: ClassEvent):
    self.exec_update(cnx, f"update course_event_details_class set duration_m={event.duration_m} where event_id={event.id}")

  def update_event_details_test(self, cnx, event: TestEvent):
    self.exec_update(cnx, f"update course_event_details_class set duration_m={event.duration_m}, configs='{json.dumps(event.to_dict_configs())}' where event_id={event.id}")

  def update_event_details_assignment(self, cnx, event: AssignmentEvent):
    pass
    # self.exec_update(cnx, f"update course_event_details_assignment set info='{event.info}' where event_id={event.id}")

  def update_event_details(self, cnx, course_id: int, event: Event):
    if event.type == E_RESOURCES:
      self.update_event_details_resources(cnx, event)
    elif event.type == E_CLASS:
      self.update_event_details_class(cnx, event)
    elif event.type == E_TEST:
      self.update_event_details_test(cnx, event)
    elif event.type == E_ASSIGNMENT:
      self.update_event_details_assignment(cnx, event)

  def update_event(self, cnx, course_id: int, event: Event):
    self.update_event_base(cnx, course_id, event)
    self.update_event_details(cnx, course_id, event)

  def update_events(self, course_id: int, events: list[Event]):
    cnx = self.get_cnx()
    for event in events:
      self.update_event(cnx, course_id, event)
    cnx.commit()

  def remove_event(self, cnx, course_id: int, event: Event):
    deleted_rows_d = self.exec_update(cnx, f"delete from course_event_details_{event_types_str[event.type]} where event_id={event.id}")
    deleted_rows_b = self.exec_update(cnx, f"delete from course_event where course_id={course_id} and id={event.id} and event_type_id={event.type}")
    if deleted_rows_b != 1 or deleted_rows_d != 1:
      logger.warning(f"When remove enent [{event.id} - {event_types_str[event.type]}] from course {course_id}, got removed {deleted_rows_b} & {deleted_rows_d}")

  def remove_events(self, course_id: int, events: list[Event]):
    cnx = self.get_cnx()
    for event in events:
      self.remove_event(cnx, course_id, event)
    cnx.commit()
  
  def get_event_submitions(self, course_id: int):
    cnx = self.get_cnx()
    submitions: dict[int, dict] = {}
    for submition in self.exec_select(cnx, f"select ces.id, ces.event_id, ces.user_id, ces.submition, ces.result from course_event_submition ces right join course_event ce on ces.event_id = ce.id where ce.course_id={course_id}"):
      submition_id = submition[0]
      event_id = submition[1]
      user_id = submition[2]
      submition_d = {"id": submition_id, "submition": json.loads(submition[3]), "result": submition[4]}
      if submitions.get(event_id, None) is None:
        submitions[event_id] = {}
      submitions[event_id][user_id] = submition_d
    return submitions
  
  def save_event_submition(self, course_id: int, event_id: int, user_id: str, submition: dict, result):
    cnx = self.get_cnx()
    self.exec_insert(cnx, f"insert into course_event_submition (event_id, user_id, submition {',result' if result is not None else ''}) values({event_id}, '{user_id}', '{json.dumps(submition)}'{',{}'.format(result) if result is not None else ''})")
    cnx.commit()
