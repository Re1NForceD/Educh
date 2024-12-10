import unittest
import bcrypt
import base64

from server_logic.logic import Logic
from server_storage.mysql_storage import MySQLStorage

class ServerLogicTests(unittest.TestCase):
  def setUp(self):
    self.correct_config = {
      "db_host": "localhost",
      "db_port": "3306",
      "db_name": "educh_db",
      "db_user": "root",
      "db_password": "12345"
    }
    
    storage = MySQLStorage(self.correct_config)
    self.logic = Logic({}, storage, None)
    
  def test_create_and_auth_course(self):
    course_name = "test_1"
    course_id, course_auth_key = \
          self.logic.create_course(course_name)
    self.assertEqual(
      course_id, 
      self.logic.verify_app(course_auth_key)
    )
