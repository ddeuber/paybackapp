from test.basecase import LoggedInBaseCase
import json
from database import Group, GroupAccess, User, Transaction
from resources.errors import errors

transaction1 = {
            'payer': 'fetteli',
            'amount': 200.0,
            'comment': 'nüt',
            'timestamp': 1604346680699,
            'involved': [
                'osmaan',
                'fetteli'
            ]
        }


class AddTransactionTest(LoggedInBaseCase):
    def test_add_single_transaction(self):
        body = json.dumps(transaction1)
        response = self.app.post('/addtransaction/1', headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.token}, data=body)
        self.assertEqual(201, response.status_code)
        expected_response = {'added transaction': {'payer': 'fetteli', 'amount': 200.0, 'comment': 'nüt', 'timestamp': 1604346680699, 'involved': ['osmaan', 'fetteli']}}
        self.assertEqual(expected_response, response.json)

    def tearDown(self):
        creation_timestamp = 1604346680699
        transaction = Transaction.query.filter_by(creation_timestamp=creation_timestamp).first()
        if transaction is not None:
            # Involved need to be removed as well since there are foreign key constraints
            for involved in transaction.involved:
                self.db.session.delete(involved)
            self.db.session.delete(transaction)
        self.db.session.commit()


class DebtTest(LoggedInBaseCase):
    def test_debt_calculation(self):
        group_id = 1
        response = self.app.get('/debts/' + str(group_id), headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(200, response.status_code)
        expected_response = {'osmaan': {'spent': 100.0, 'owes': 145.0, 'credit': -45.0}, 'fetteli': {'spent': 210.0, 'owes': 145.0, 'credit': 65.0}, "hell's angels": {'spent': 0, 'owes': 20.0, 'credit': -20.0}}
        self.assertEqual(expected_response, response.json)


class ParticipantsTest(LoggedInBaseCase):
    def test_group_participants(self):
        group_id = 1
        response = self.app.get('/participants/' + str(group_id), headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(200, response.status_code)
        excpected_response = {'participants': ['osmaan', 'fetteli', "hell's angels"]}
        self.assertEqual(excpected_response, response.json)

    def test_group_participants_empty(self):
        group_id = 2
        response = self.app.get('/participants/' + str(group_id), headers={'Authorization': 'Bearer ' + self.token})
        self.assertEqual(200, response.status_code)
        excpected_response = {'participants': []}
        self.assertEqual(excpected_response, response.json)