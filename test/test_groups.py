from test.basecase import LoggedInBaseCase
import json
from database import Group, GroupAccess, User, db
from resources.errors import errors

class AddGroupTest(LoggedInBaseCase):
    def test_successful_refresh(self):
        body = json.dumps({'name': 'testgroup'})
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

        