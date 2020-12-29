from test.basecase import BaseCase
import json
from database import User

class SignupTest(BaseCase):
    
    def test_successful_signup(self):
        self.email = 'deuber@test.ch'
        body = json.dumps({'email': self.email, 'password': 'test'})
        response = self.app.post('/signup', headers={'Content-Type': 'application/json'}, data=body)
        self.assertEqual(201, response.status_code)

    def tearDown(self):
        user = User.query.filter_by(email=self.email).first()
        self.db.session.delete(user)
        self.db.session.commit()
        

