import unittest
import bcrypt
import base64

from course_classes import *
from server_storage.mysql_storage import MySQLStorage

class MySQLTests(unittest.TestCase):
  def setUp(self):
    self.correct_config = {
      "db_host": "localhost",
      "db_port": "3306",
      "db_name": "educh_db",
      "db_user": "root",
      "db_password": "12345"
    }
    
    password = 'password123'
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)

    self.test_course_data = (
      "test_course_tests", 
      hash.decode('utf-8'), bytes
    )
    self.storage = MySQLStorage(self.correct_config)

  def test_invalid_config(self):
    with self.assertRaises(Exception) as cm:
      MySQLStorage({})
          
  def test_invalid_config_db_data(self):
    config = self.correct_config.copy()
    config["db_password"] = ""
    with self.assertRaises(ConnectionError) as cm:
      MySQLStorage(config)
  
  def test_creation_success(self):
    MySQLStorage(self.correct_config)
  
  def test_general_methods_success(self):
    cnx = self.storage.get_cnx()

    # insert
    self.test_course_id = self.storage.exec_insert(cnx, f"insert into course (name, hash) values ('{self.test_course_data[0]}', '{self.test_course_data[1]}')")
    
    # select
    data = self.storage.exec_select(cnx, f"SELECT name, hash from course where id={self.test_course_id}")
    self.assertEqual(len(data), 1, f"failed rows: {data}")
    self.assertEqual(len(data[0]), 2)
    self.assertEqual(data[0][0], self.test_course_data[0])
    self.assertEqual(data[0][1], self.test_course_data[1])

    # update
    new_course_name = self.test_course_data[0] + '1'
    amount = self.storage.exec_update(cnx, f"update course set name='{new_course_name}' where id={self.test_course_id}")
    self.assertEqual(amount, 1)

    data = self.storage.exec_select(cnx, f"SELECT name from course where id={self.test_course_id}")
    self.assertEqual(data[0][0], new_course_name)

    amount = self.storage.exec_update(cnx, f"update course set name='{self.test_course_data[0]}' where id={self.test_course_id}")
    self.assertEqual(amount, 1)

    data = self.storage.exec_select(cnx, f"SELECT name from course where id={self.test_course_id}")
    self.assertEqual(data[0][0], self.test_course_data[0])
    
    cnx.commit()
    
    # creds
    hash_db = self.storage.get_course_auth_data(self.test_course_id)

    # bytes = '{}{}'.format(data[0][1],data[0][0]).encode('utf-8') # make hash from <name+id>
    bytes = self.test_course_data[2] # make hash from <name>
    hash = hash_db.encode('utf-8')
    self.assertTrue(bcrypt.checkpw(bytes, hash))

    # get course data
    course: Course = self.storage.get_course_data(self.test_course_id)
    self.assertEqual(self.test_course_id, course.id)
    self.assertEqual(self.test_course_data[0], course.name)
    self.assertEqual(None, course.channel_id)
    self.assertEqual(None, course.started_at)
    self.assertEqual(0, len(course.events))
    self.assertEqual(0, len(course.submissions_by_id))
    self.assertEqual(0, len(course.submissions))
    self.assertEqual(0, len(course.users))
