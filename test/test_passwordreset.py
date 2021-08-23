from test.basecase import LoggedInBaseCase, BaseCase
import json
from database import Group, GroupAccess, User
from appconfig import mail
from resources.errors import errors
import time 

class ForgotPasswordTest(BaseCase):
    def test_forgot_password_mail(self):
        with mail.record_messages() as outbox: # keep mails in outbox
            body = json.dumps({'email': 'test@test.ch'})
            response = self.app.post('/forgotpassword', data=body)
            self.assertEqual(200, response.status_code)
            time.sleep(5) # wait for mail to be sent
            self.assertEqual(1, len(outbox))

class ChangePasswordTest(LoggedInBaseCase):
    def test_change_password(self):
        body = json.dumps({'password': 'newpassword'})
        response = self.app.post('/resetpassword', headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.token}, data=body)
        self.assertEqual(200, response.status_code)
        login_body = json.dumps({'email': 'test@test.ch', 'password': 'newpassword'})
        login_response = self.app.post('/login', headers={'Content-Type': 'application/json'}, data=login_body)
        self.assertEqual(200, login_response.status_code)

    # try to change password with a nonfresh token, which should fail
    def test_change_password_nonfresh(self):
        body = json.dumps({'password': 'newpassword'})
        refresh_response = self.app.post('/refresh', headers={'Authorization': 'Bearer ' + self.refresh_token})
        nonfresh_token = refresh_response.json.get('access_token')
        response = self.app.post('/resetpassword', headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + nonfresh_token}, data=body)
        self.assertEqual(401, response.status_code)




