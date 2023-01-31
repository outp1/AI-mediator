import unittest
import main

class TestWebApp(unittest.TestCase):
 def setUp(self):
 self.app = main.app.test_client()

 def test_index(self):
 response = self.app.get('/')
 self.assertEqual(response.status_code, 200)
 self.assertIn(b'Welcome to my web app!', response.data)

if name == 'main':
 unittest.main()
