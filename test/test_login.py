
from test.basecase import BaseCase
import json
from database import User

class SignupTest(BaseCase):
    def test_successful_signup(self):
        body = json.dumps({'email': 'test@test.ch', 'password': 'test'})
        response = self.app.post('/login', headers={'Content-Type': 'application/json'}, data=body)
        self.assertEqual(200, response.status_code)
        self.assertIn('access_token', response.json)
        self.assertIn('refresh_token', response.json)