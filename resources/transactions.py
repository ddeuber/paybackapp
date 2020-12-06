import flask
import flask_restful
from database import db, Transaction, Involved, Group, User
from datetime import datetime
from resources.errors import TransactionSchemaError, GroupNotFoundError, NoInvolvedError, InvolvedNotIterableError, TimestampTypeError, SchemaValidationError
from sqlalchemy.exc import IntegrityError, InterfaceError

### Utility functions

# Adds single transaction to database without commit.
def add_transaction(transaction, group):
    transaction_for_database = Transaction(transaction, group)
    db.session.add(transaction_for_database)
    # Add involved
    at_least_one_participant = False
    participants = transaction.get('involved')
    if not isinstance(participants, list):
        raise SchemaValidationError
    for participant in participants: 
        at_least_one_participant = True
        involved = Involved(transaction=transaction_for_database, participant=participant)
        db.session.add(involved)
    if not at_least_one_participant:
        raise NoInvolvedError


### Resources 

# add a single transaction
class AddTransaction(flask_restful.Resource):
    def post(self, group_id):
        transaction_from_request = flask.request.get_json(force=True)
        if not isinstance(transaction_from_request, dict):
            raise SchemaValidationError
        group = Group.query.get(group_id)
        if group is None:
            raise GroupNotFoundError
        try:
            add_transaction(transaction_from_request, group)
            db.session.commit()
        except (IntegrityError, InterfaceError):
            raise TransactionSchemaError
        return {'added transaction': transaction_from_request}, 201

# Get list of all transactions in group
class TransactionList(flask_restful.Resource):
    def get(self, group_id):
        transactions = []
        group = Group.query.get(group_id)
        if group is None:
            raise GroupNotFoundError
        for t in group.transactions:
            transactions.append(t.to_dict())
        return transactions

# Upload new transactions and download transaction uploaded after timestamp
class TransactionUpdate(flask_restful.Resource):
    def post(self, group_id):
        request_transaction_dict = flask.request.get_json(force=True)
        if not isinstance(request_transaction_dict, dict):
            raise SchemaValidationError
        timestamp = request_transaction_dict.get('timestamp')
        if not isinstance(timestamp, int):
            raise TimestampTypeError
        # Get transactions added after timestamp
        group = Group.query.get(group_id)
        if group is None:
            raise GroupNotFoundError 
        return_transaction_list = [t.to_dict() for t in Transaction.query.join(Group).filter(Group.id==group.id).filter(Transaction.server_timestamp>timestamp)]
        # Add new transactions
        try:
            for transaction in request_transaction_dict.get('transactions'):
                add_transaction(transaction, group)
            db.session.commit()
        except (IntegrityError, InterfaceError, TypeError):
            raise TransactionSchemaError
        return {"server_timestamp": int(datetime.now().timestamp()*1000), "transactions": return_transaction_list}


# Calculate depts for each participant
class Debts(flask_restful.Resource):
    def get(self, group_id):
        output = {}
        group = Group.query.get(group_id)
        if group is None:
            raise GroupNotFoundError
        for t in group.transactions:
            t_dict = t.to_dict()
            # create entry for every member that's not yet in output
            for member in [t_dict['payer']] + t_dict['involved']:
                if member not in output:
                    output[member] = {'spent': 0, 'owes': 0}
            output[t_dict['payer']]['spent'] += t_dict['amount']
            for member in t_dict['involved']:
                output[member]['owes'] += t_dict['amount'] / len(t_dict['involved'])
        for member in output:
            output[member]['credit'] = output[member]['spent'] - output[member]['owes']
        return output            