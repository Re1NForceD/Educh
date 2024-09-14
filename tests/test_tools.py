import unittest
import bcrypt

class ToolsTests(unittest.TestCase):
    def setUp(self):
        pass

    def test_brypt_success(self):
        password = 'password123'
        bytes = password.encode('utf-8')

        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(bytes, salt)

        self.assertTrue(bcrypt.checkpw(bytes, hash))

    def test_brypt_success(self):
        password = 'password'
        bytes = password.encode('utf-8')

        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(bytes, salt)

        userPassword =  'incorrect'
        userBytes = userPassword.encode('utf-8')

        self.assertFalse(bcrypt.checkpw(userBytes, hash))