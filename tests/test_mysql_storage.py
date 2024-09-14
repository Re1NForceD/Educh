import unittest
from storage.mysql_storage import MySQLStorage

class MySQLTests(unittest.TestCase):
    def setUp(self):
        self.correct_config = {
            "db_host": "localhost",
            "db_port": "3306",
            "db_name": "educh_db",
            "db_user": "root",
            "db_password": "12345"
        }
        self.test_course_data = (1, "dGVzdF9jb3Vyc2U=")

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
    
    def test_simple_select_success(self):
        stor = MySQLStorage(self.correct_config)
        data = stor.exec_select(stor.get_cnx(), "SELECT * from user_role")
    
    def test_simple_insert_success(self):
        storage = MySQLStorage(self.correct_config)
        cnx = storage.get_cnx()
        new_id = storage.exec_insert(cnx, "insert into user_role (name) values ('test')")
        cnx.commit()
    
    def test_simple_update_success(self):
        storage = MySQLStorage(self.correct_config)
        cnx = storage.get_cnx()
        data = storage.exec_update(cnx, "update user_role set name = 'test1' where id = 10")
        cnx.commit()
    
    def test_verify_test_course_success(self):
        storage = MySQLStorage(self.correct_config)
        session_key = storage.verify_app(*self.test_course_data)
        self.assertTrue(session_key)
    
    def test_verify_test_course_fail(self):
        storage = MySQLStorage(self.correct_config)
        name = storage.verify_app(self.test_course_data[0], "invalid_key")
        self.assertFalse(name)
