import os
import bcrypt
import logging
import mysql.connector
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
  
  def get_event(self, db_row):
    return get_event(*db_row)
  
  def get_course_data(self, course_id: int) -> Course:
    cnx = self.get_cnx()
    
    general_info = self.exec_select(
        cnx, f"select id, name, channel_id, start_date from course where id = {course_id}")
    
    if len(general_info) != 1:
      raise RuntimeError(f"invalid course info in db for: {course_id}")
    
    course = Course(id=general_info[0][0], name=general_info[0][1], channel_id=general_info[0][2], start_date=general_info[0][3])
    
    events = self.exec_select(
        cnx, f"select id, event_type_id, start_time, duration_m from course_event where course_id = {course_id}")
    if len(events):
      for event_data in events:
        course.add_event(self.get_event(event_data))
    
    users = self.exec_select(
        cnx, f"select cu.platform_id, cu.name, cu.role_id from course_user cu where cu.course_id = {course_id}")
    if len(users):
      for user_data in users:
        course.add_user(User(*user_data))

    return course
  
  def update_users(self, course_id: int, users: list[User]) -> None:
    cnx = self.get_cnx()
    for user in users:
      self.exec_insert(cnx, f"insert into course_user (course_id, platform_id, name, role_id) values({course_id}, '{user.platform_id}', '{user.name}', {user.role})")
    cnx.commit()

  def update_essensials(self, course_id: int, channel_id: str=None, start_date: datetime.datetime=None):
    values_update = []

    if channel_id is not None:
      values_update.append(f"channel_id='{channel_id}'")
    
    if start_date is not None:
      values_update.append(f"start_date='{datetime_to_str(start_date)}'")
    
    if len(values_update) == 0:
      return
    
    cnx = self.get_cnx()
    self.exec_update(cnx, f"update course set {','.join(values_update)} where id = {course_id}")
    cnx.commit()
