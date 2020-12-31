from test.basecase import LoggedInBaseCase
import json
from database import Group, GroupAccess, User
from resources.errors import errors

class AddGroupTest(LoggedInBaseCase):
    def test_successful_refresh(self):
        body = json.dumps({'name': 'newgroup'})
        response = self.app.post('/addgroup', headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.token}, data=body)
        self.assertEqual(201, response.status_code)
        group_id = response.json['id']
        self.group = Group.query.get(group_id)
        self.assertIsNotNone(self.group)
        self.group_access = GroupAccess.query.filter_by(group_id=group_id).join(User).filter_by(email=self.email).first()
        self.assertIsNotNone(self.group_access)

    def tearDown(self):
        if self.group_access is not None:
            self.db.session.delete(self.group_access)
        if self.group is not None:
            self.db.session.delete(self.group)
        self.db.session.commit()

class GetGroupsTest(LoggedInBaseCase):
    def test_get_groups(self):
        response = self.app.get('/groups', headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(200, response.status_code)
        expected_response = {'groups': [{'id': 1, 'name': 'testgroup'}, {'id': 2, 'name': 'testgroup2'}]}
        self.assertEqual(expected_response, response.json)

        
class AddUserToGroupTest(LoggedInBaseCase):
    def test_add_existing_user(self):
        email = 'test2@test.ch'
        body = json.dumps({'email': email})
        group_id = 1
        response = self.app.post('/addusertogroup/' + str(group_id), headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.token}, data=body)
        self.assertEqual(200, response.status_code)
        self.group_access = GroupAccess.query.filter_by(group_id=group_id).join(User).filter_by(email=email).first()
        self.assertIsNotNone(self.group_access)

    def tearDown(self):
        if self.group_access is not None:
            self.db.session.delete(self.group_access)
            self.db.session.commit() 


class AddUserToWrongGroupTest(LoggedInBaseCase):
    def test_add_existing_user(self):
        email = 'test2@test.ch'
        body = json.dumps({'email': email})
        group_id = 3
        response = self.app.post('/addusertogroup/' + str(group_id), headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.token}, data=body)
        self.assertEqual(403, response.status_code)
        self.assertEqual(errors['NoAccessToGroupError']['message'], response.json['message'])


class LeaveGroupTest(LoggedInBaseCase):
    def test_leave_group(self):
        self.group_id = 1
        response = self.app.post('/leavegroup/' + str(self.group_id), headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(200, response.status_code)
        self.group_access = GroupAccess.query.filter_by(group_id=self.group_id).join(User).filter_by(email=self.email).first()
        self.assertIsNone(self.group_access)

    def tearDown(self):
        if self.group_access is None:
            user = User.query.filter_by(email=self.email).first()
            group = Group.query.get(self.group_id)
            group_access = GroupAccess(id=1, group=group, user=user)
            self.db.session.add(group_access)
            self.db.session.commit()


class LeaveWrongGroupTest(LoggedInBaseCase):
    def test_leave_wrong_group(self):
        group_id = 3
        response = self.app.post('/leavegroup/' + str(group_id), headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(403, response.status_code)
        self.assertEqual(errors['NoAccessToGroupError']['message'], response.json['message'])



       