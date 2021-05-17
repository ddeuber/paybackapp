import flask
from flask_restful import Resource
from database import db, Transaction, Involved, Group, User
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from resources.errors import TransactionSchemaError, NoInvolvedError, InvolvedNotIterableError, TimestampTypeError, SchemaValidationError
from resources.groups import get_group, assert_access_to_group
from resources.login import get_user
from sqlalchemy.exc import IntegrityError, InterfaceError

### Utility functions

# Adds single transaction to database without commit.
def add_transaction(transaction, group, creator):
    transaction_for_database = Transaction(transaction, group, creator)
    db.session.add(transaction_for_database)
    # Add involved
    at_least_one_participant = False
    participants = transaction.get('involved')
    if not isinstance(participants, list):
        raise InvolvedNotIterableError 
    for participant in participants: 
        at_least_one_participant = True
        involved = Involved(transaction=transaction_for_database, participant=participant)
        db.session.add(involved)
    if not at_least_one_participant:
        raise NoInvolvedError


### Resources 

# Add a single transaction
class AddTransaction(Resource):
    @jwt_required
    def post(self, group_id):
        transaction_from_request = flask.request.get_json(force=True)
        group = get_group(group_id)
        user = get_user(get_jwt_identity())
        assert_access_to_group(user.id, group.id)
        try:
            add_transaction(transaction_from_request, group, user)
            db.session.commit()
        except (IntegrityError, InterfaceError):
            raise TransactionSchemaError
        return {'added transaction': transaction_from_request}, 201


# Get list of all transactions in group
class TransactionList(Resource):
    @jwt_required()
    def post(self, group_id):
        body = flask.request.get_json(force=True) # body contains optional filter parameters payer, participant, limit and offset
        if not isinstance(body, dict):
           raise SchemaValidationError
        transactions = []
        group = get_group(group_id)
        user = get_user(get_jwt_identity())
        assert_access_to_group(user.id, group.id)
        transaction_query = Transaction.query.filter_by(group_id=group.id)
        payer = body.get('payer')
        if payer is not None:
            transaction_query = transaction_query.filter_by(payer=payer)
        participant = body.get('participant')
        if participant is not None:
            transaction_query = transaction_query.join(Involved).filter_by(participant=participant)
        group_transactions = transaction_query.order_by(Transaction.id.desc()).limit(body.get('limit')).offset(body.get('offset'))
        for t in group_transactions:
            transactions.append(t.to_dict())
        return transactions


# Upload new transactions and download transaction uploaded after timestamp
class TransactionUpdate(Resource):
    @jwt_required()
    def post(self, group_id):
        request_transaction_dict = flask.request.get_json(force=True)
        if not isinstance(request_transaction_dict, dict):
            raise SchemaValidationError
        timestamp = request_transaction_dict.get('timestamp')
        if not isinstance(timestamp, int):
            raise TimestampTypeError
        # Add new transactions
        group = get_group(group_id)
        user = get_user(get_jwt_identity())
        assert_access_to_group(user.id, group.id)
        try:
            for transaction in request_transaction_dict.get('transactions'):
                add_transaction(transaction, group, user)
            db.session.commit()
        except (IntegrityError, InterfaceError, TypeError):
            raise TransactionSchemaError
        # Get transactions added after timestamp
        return_transaction_list = [t.to_dict() for t in Transaction.query.join(Group).filter(Group.id==group.id).filter(Transaction.server_timestamp>timestamp)]
        return {"server_timestamp": int(datetime.now().timestamp()*1000), "transactions": return_transaction_list}


# Calculate depts for each participant
class Debts(Resource):
    @jwt_required()
    def get(self, group_id):
        output = {}
        group = get_group(group_id)
        user = get_user(get_jwt_identity())
        assert_access_to_group(user.id, group.id)
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


# Get all participants of group
class Participants(Resource):
    @jwt_required()
    def get(self, group_id):
        group = get_group(group_id)
        user = get_user(get_jwt_identity())
        assert_access_to_group(user.id, group.id)
        participants = Involved.query.join(Transaction).filter_by(group_id=group_id).with_entities(Involved.participant).distinct()
        response = {'participants': []}
        for p in participants:
            response['participants'].append(p[0])
        return response 


