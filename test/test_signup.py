from test.basecase import BaseCase
import json
from database import User
from resources.errors import errors

class SignupTest(BaseCase):
    
    def test_successful_signup(self):
        email = 'signmeup@test.ch'
        body = json.dumps({'email': email, 'password': 'test'})
        response = self.app.post('/signup', headers={'Content-Type': 'application/json'}, data=body)
        self.assertEqual(201, response.status_code)
        user = User.query.filter_by(email=email).first()
        self.assertIsNotNone(user)
        self.user = user

    def tearDown(self):
        try: 
            self.db.session.delete(self.user)
            self.db.session.commit()
        except:
            print('Could not delete user in tearDown')
        

class BadSignupTest(BaseCase):

    def test_bad_email_signup(self):
        email = 'blabla'
        body = json.dumps({'email': email, 'password': 'test'})
        response = self.app.post('/signup', headers={'Content-Type': 'application/json'}, data=body)
        self.assertEqual(400, response.status_code)
        self.assertEqual(errors['InvalidEmailAddressError']['msg'], response.json['msg'])

    def test_no_email_signup(self):
        body = json.dumps({'password': 'test'})
        response = self.app.post('/signup', headers={'Content-Type': 'application/json'}, data=body)
        self.assertEqual(400, response.status_code)
        self.assertEqual(errors['SchemaValidationError']['msg'], response.json['msg'])

    def test_no_password_signup(self):
        body = json.dumps({'email': 'signmeup@test.ch'})
        response = self.app.post('/signup', headers={'Content-Type': 'application/json'}, data=body)
        self.assertEqual(400, response.status_code)
        self.assertEqual(errors['SchemaValidationError']['msg'], response.json['msg'])

