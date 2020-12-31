
from test.basecase import BaseCase
import json
from database import User
from resources.errors import errors

class LoginTest(BaseCase):
    def test_successful_login(self):
        body = json.dumps({'email': 'test@test.ch', 'password': 'test'})
        response = self.app.post('/login', headers={'Content-Type': 'application/json'}, data=body)
        self.assertEqual(200, response.status_code)
        self.assertIn('access_token', response.json)
        self.assertIn('refresh_token', response.json)

    def test_wrong_password(self):
        body = json.dumps({'email': 'test@test.ch', 'password': 'wrong'})
        response = self.app.post('/login', headers={'Content-Type': 'application/json'}, data=body)
        self.assertEqual(401, response.status_code)
        self.assertEqual(errors['InvalidLoginError']['message'], response.json['message'])

    def test_bad_user(self):
        body = json.dumps({'email': 'new@test.ch', 'password': 'right'})
        response = self.app.post('/login', headers={'Content-Type': 'application/json'}, data=body)
        self.assertEqual(401, response.status_code)
        self.assertEqual(errors['InvalidLoginError']['message'], response.json['message'])


class RefreshTest(BaseCase):
    def test_successful_refresh(self):
        body = json.dumps({'email': 'test@test.ch', 'password': 'test'})
        response = self.app.post('/login', headers={'Content-Type': 'application/json'}, data=body)
        refresh_token = response.json['refresh_token']
        refresh_response = self.app.post('/refresh', headers={'Authorization': 'Bearer ' + refresh_token})
        self.assertEqual(200, refresh_response.status_code)
        self.assertIn('access_token', refresh_response.json)

