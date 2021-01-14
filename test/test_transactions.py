from test.basecase import LoggedInBaseCase
import json
from database import Group, GroupAccess, User, Transaction
from resources.errors import errors



class AddTransactionTest(LoggedInBaseCase):
    def test_add_single_transaction(self):
        test_transaction = {'payer': 'fetteli', 'amount': 200.0, 'comment': 'nüt', 'timestamp': 1604346680699, 'involved': [ 'osmaan', 'fetteli' ]}
        body = json.dumps(test_transaction)
        group_id = 1
        response = self.app.post('/addtransaction/' + str(group_id), headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.token}, data=body)
        self.assertEqual(201, response.status_code)
        expected_response = {'added transaction': {'payer': 'fetteli', 'amount': 200.0, 'comment': 'nüt', 'timestamp': 1604346680699, 'involved': ['osmaan', 'fetteli']}}
        self.assertEqual(expected_response, response.json)


class GetTransactionListTest(LoggedInBaseCase):
    def get_transaction_list(self, filters, expected_response):
        body = json.dumps(filters)
        group_id = 1
        response = self.app.post('/transactions/' + str(group_id), headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.token}, data=body)
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_response, response.json)

    def test_get_unfiltered_transaction_list(self):
        expected_response = [{'creator': 'test@test.ch', 'payer': 'fetteli', 'amount': 100.0, 'comment': 'nüt', 'timestamp': 1604346680680, 'involved': ['osmaan', 'fetteli']}, {'creator': 'test@test.ch', 'payer': 'fetteli', 'amount': 60.0, 'comment': 'nüt', 'timestamp': 1604346680680, 'involved': ['osmaan', 'fetteli', "hell's angels"]}, {'creator': 'test@test.ch', 'payer': 'fetteli', 'amount': 50.0, 'comment': 'nüt', 'timestamp': 1604346680680, 'involved': ['osmaan', 'fetteli']}, {'creator': 'test@test.ch', 'payer': 'osmaan', 'amount': 100.0, 'comment': 'nüt', 'timestamp': 1604346680629, 'involved': ['osmaan', 'fetteli']}] 
        self.get_transaction_list({}, expected_response)
        
    def test_get_offset_transaction_list(self):
        filter = {'offset': 1}
        expected_response = [{'creator': 'test@test.ch', 'payer': 'fetteli', 'amount': 60.0, 'comment': 'nüt', 'timestamp': 1604346680680, 'involved': ['osmaan', 'fetteli', "hell's angels"]}, {'creator': 'test@test.ch', 'payer': 'fetteli', 'amount': 50.0, 'comment': 'nüt', 'timestamp': 1604346680680, 'involved': ['osmaan', 'fetteli']}, {'creator': 'test@test.ch', 'payer': 'osmaan', 'amount': 100.0, 'comment': 'nüt', 'timestamp': 1604346680629, 'involved': ['osmaan', 'fetteli']}]
        self.get_transaction_list(filter, expected_response)

    def test_get_limited_transaction_list(self):
        filter = {'limit': 2}
        expected_response = [{'creator': 'test@test.ch', 'payer': 'fetteli', 'amount': 100.0, 'comment': 'nüt', 'timestamp': 1604346680680, 'involved': ['osmaan', 'fetteli']}, {'creator': 'test@test.ch', 'payer': 'fetteli', 'amount': 60.0, 'comment': 'nüt', 'timestamp': 1604346680680, 'involved': ['osmaan', 'fetteli', "hell's angels"]}]
        self.get_transaction_list(filter, expected_response)

    def test_get_transaction_list_by_payer(self):
        filter = {'payer': 'osmaan'}
        expected_response = [{'creator': 'test@test.ch', 'payer': 'osmaan', 'amount': 100.0, 'comment': 'nüt', 'timestamp': 1604346680629, 'involved': ['osmaan', 'fetteli']}]
        self.get_transaction_list(filter, expected_response)
    
    def test_get_transaction_list_by_participant(self):
        filter = {'participant': "hell's angels"}
        expected_response = [{'creator': 'test@test.ch', 'payer': 'fetteli', 'amount': 60.0, 'comment': 'nüt', 'timestamp': 1604346680680, 'involved': ['osmaan', 'fetteli', "hell's angels"]}] 
        self.get_transaction_list(filter, expected_response)

    def test_get_filtered_transaction_list(self):
        filter = {'payer': 'fetteli', 'limit':1, 'offset':1}
        expected_response =  [{'creator': 'test@test.ch', 'payer': 'fetteli', 'amount': 60.0, 'comment': 'nüt', 'timestamp': 1604346680680, 'involved': ['osmaan', 'fetteli', "hell's angels"]}]
        self.get_transaction_list(filter, expected_response)


class TransactionUpdateTestTimeZero(LoggedInBaseCase):
    def test_transaction_update_time_zero(self):
        update_dict = {"timestamp":0,"transactions":[{"payer":"osmaan","amount":100,"comment":"nüt","timestamp":1604346680629,"group_name":"213","involved":["osmaan","fetteli"]},{"payer":"osmaan","amount":100,"comment":"nüt","timestamp":1604346680629,"group_name":"213","involved":["osmaan","fetteli"]}]} 
        body = json.dumps(update_dict)
        group_id = 1
        response = self.app.post('/update/' + str(group_id), headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.token}, data=body)
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.json.get('server_timestamp'))
        self.assertEqual(6, Transaction.query.filter_by(group_id=group_id).count())
        expected_transactions = [{'creator': 'test@test.ch', 'payer': 'osmaan', 'amount': 100.0, 'comment': 'nüt', 'timestamp': 1604346680629, 'involved': ['osmaan', 'fetteli']}, {'creator': 'test@test.ch', 'payer': 'fetteli', 'amount': 50.0, 'comment': 'nüt', 'timestamp': 1604346680680, 'involved': ['osmaan', 'fetteli']}, {'creator': 'test@test.ch', 'payer': 'fetteli', 'amount': 60.0, 'comment': 'nüt', 'timestamp': 1604346680680, 'involved': ['osmaan', 'fetteli', "hell's angels"]}, {'creator': 'test@test.ch', 'payer': 'fetteli', 'amount': 100.0, 'comment': 'nüt', 'timestamp': 1604346680680, 'involved': ['osmaan', 'fetteli']}, {'creator': 'test@test.ch', 'payer': 'osmaan', 'amount': 100.0, 'comment': 'nüt', 'timestamp': 1604346680629, 'involved': ['osmaan', 'fetteli']}, {'creator': 'test@test.ch', 'payer': 'osmaan', 'amount': 100.0, 'comment': 'nüt', 'timestamp': 1604346680629, 'involved': ['osmaan', 'fetteli']}]
        self.assertEqual(expected_transactions, response.json.get('transactions'))


class TransactionUpdateTestTimestamped(LoggedInBaseCase):
    def test_transaction_update(self):
        update_dict = {"timestamp":1609412103497,"transactions":[{"payer":"osmaan","amount":100,"comment":"nüt","timestamp":1604346680629,"group_name":"213","involved":["osmaan","fetteli"]},{"payer":"osmaan","amount":100,"comment":"nüt","timestamp":1604346680629,"group_name":"213","involved":["osmaan","fetteli"]}]} 
        body = json.dumps(update_dict)
        group_id = 1
        response = self.app.post('/update/' + str(group_id), headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + self.token}, data=body)
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response.json.get('server_timestamp'))
        self.assertEqual(6, Transaction.query.filter_by(group_id=group_id).count())
        expected_transaction = [{'creator': 'test@test.ch', 'payer': 'fetteli', 'amount': 100.0, 'comment': 'nüt', 'timestamp': 1604346680680, 'involved': ['osmaan', 'fetteli']}, {'creator': 'test@test.ch', 'payer': 'osmaan', 'amount': 100.0, 'comment': 'nüt', 'timestamp': 1604346680629, 'involved': ['osmaan', 'fetteli']}, {'creator': 'test@test.ch', 'payer': 'osmaan', 'amount': 100.0, 'comment': 'nüt', 'timestamp': 1604346680629, 'involved': ['osmaan', 'fetteli']}]
        self.assertEqual(expected_transaction, response.json.get('transactions'))


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

    
