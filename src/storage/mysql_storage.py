import os
import bcrypt
import logging
import mysql.connector
from mysql.connector import Error

from .storage import DataStorage

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
