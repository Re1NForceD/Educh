import unittest
from storage.mysql_storage import MySQLStorage
import bcrypt
import base64

class MainLogicTests(unittest.TestCase):
    def setUp(self):
        self.correct_config = {
            "db_host": "localhost",
            "db_port": "3306",
            "db_name": "educh_db",
            "db_user": "root",
            "db_password": "12345"
        }
        self.storage = MySQLStorage(self.correct_config)
    
    def test_select_test_course(self):
        cnx = self.storage.get_cnx()
        data = self.storage.exec_select(cnx, "SELECT id, name from course where id = 1")

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0][0], 1)
        self.assertEqual(data[0][1], "test_course")
    
    def test_test_course_creds(self):
        cnx = self.storage.get_cnx()
        data = self.storage.exec_select(cnx, "SELECT id, name, hash from course where id = 1")

        # bytes = '{}{}'.format(data[0][1],data[0][0]).encode('utf-8') # make hash from <name+id>
        bytes = base64.b64encode(data[0][1].encode('utf-8')) # make hash from <name>
        hash = data[0][2].encode('utf-8')
        self.assertTrue(bcrypt.checkpw(bytes, hash))