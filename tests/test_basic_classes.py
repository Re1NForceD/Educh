import unittest
import bcrypt
import base64

from course_classes import *
from server_logic.logic import Logic
from server_storage.mysql_storage import MySQLStorage

class BasicClassesTests(unittest.TestCase):
  def setUp(self):
    pass
  
  def test_create_course_params_success(self):
    course_id = 1
    course_name = "test_course"

    course: Course = Course(id=course_id, name=course_name)

    self.assertEqual(course_id, course.id)
    self.assertEqual(course_name, course.name)
    self.assertEqual(None, course.channel_id)
    self.assertEqual(None, course.started_at)
    self.assertEqual(0, len(course.events))
    self.assertEqual(0, len(course.submissions_by_id))
    self.assertEqual(0, len(course.submissions))
    self.assertEqual(0, len(course.users))

  def test_create_course_params_failed(self):
    course_id = None
    course_name = "test_course"
    with self.assertRaises(RuntimeError) as cm:
      course: Course = Course(id=course_id, name=course_name)

  def test_create_course_dict_success(self):
    course_id = 1
    course_name = "test_course"
    course_data = {'id': course_id, 'name': course_name, 'channel_id': None, 'started_at': None, 'events': [], 'users': []}

    course: Course = Course(data=course_data)

    self.assertEqual(course_id, course.id)
    self.assertEqual(course_name, course.name)
    self.assertEqual(None, course.channel_id)
    self.assertEqual(None, course.started_at)
    self.assertEqual(0, len(course.events))
    self.assertEqual(0, len(course.submissions_by_id))
    self.assertEqual(0, len(course.submissions))
    self.assertEqual(0, len(course.users))

  def test_create_course_dict_failed(self):
    course_data = {'name': 'test_course_tests', 'channel_id': None, 'started_at': None, 'events': [], 'users': []}
    with self.assertRaises(KeyError) as cm:
      course: Course = Course(data=course_data)
