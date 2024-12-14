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
  
  def test_collect_course_submissions_success(self):
    course_id = 1
    course_name = "test_course"

    course: Course = Course(id=course_id, name=course_name)

    master: User = User("master", "Master", 4)
    course.add_user(master)

    user1: User = User("user1", "User1", 2)
    course.add_user(user1)

    c_subs_b_1, c_subs_b_2 = len(course.submissions), len(course.submissions_by_id)
    self.assertEqual(c_subs_b_1, c_subs_b_2)

    for i in range(1, 20, 2):
      event1: Event = ResourcesEvent(i, f"event{i}", datetime.datetime.now(), f"event{i} info", True)
      course.add_event(event1)
      submission_1_id = i
      submission_1 = {"info": f"test submission{i}"}
      
      c_subs_b_1, c_subs_b_2 = len(course.submissions), len(course.submissions_by_id)
      course.colect_submission({submission_1_id: [event1.id, user1.platform_id, {"id": submission_1_id, "submission": submission_1, "submitter_id": master.platform_id, "result": 20}]})
      c_subs_a_1, c_subs_a_2 = len(course.submissions), len(course.submissions_by_id)

      self.assertEqual(c_subs_b_1, c_subs_b_2, f"iter {i}: {course.submissions} ||\n|| {course.submissions_by_id}")
      self.assertEqual(c_subs_a_1, c_subs_a_2, f"iter {i}: {course.submissions} ||\n|| {course.submissions_by_id}")
      self.assertEqual(c_subs_a_1 - c_subs_b_1, 1, f"iter {i}: {course.submissions} ||\n|| {course.submissions_by_id}")
      self.assertEqual(c_subs_a_2 - c_subs_b_2, 1, f"iter {i}: {course.submissions} ||\n|| {course.submissions_by_id}")

      event2: Event = AssignmentEvent(i+1, f"event{i+1}", datetime.datetime.now(), f"event{i+1} info", True)
      course.add_event(event2)
      submission_2_id = i+1
      submission_2 = {"info": f"test submission{submission_2_id}"}

      c_subs_b_3, c_subs_b_4 = len(course.submissions), len(course.submissions_by_id)
      course.colect_submission({submission_2_id: [event2.id, user1.platform_id, {"id": submission_2_id, "submission": submission_2}]})
      c_subs_a_3, c_subs_a_4 = len(course.submissions), len(course.submissions_by_id)

      self.assertEqual(c_subs_a_3, c_subs_a_4, f"iter {i}: {course.submissions} ||\n|| {course.submissions_by_id}")
      self.assertEqual(c_subs_b_3, c_subs_b_4, f"iter {i}: {course.submissions} ||\n|| {course.submissions_by_id}")
      self.assertEqual(c_subs_a_3 - c_subs_b_3, 1, f"iter {i}: {course.submissions} ||\n|| {course.submissions_by_id}")
      self.assertEqual(c_subs_a_4 - c_subs_b_4, 1, f"iter {i}: {course.submissions} ||\n|| {course.submissions_by_id}")
