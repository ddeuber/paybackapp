import flask
from flask_restful import Resource
from database import db, Transaction, Involved, Group, User
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from resources.errors import TransactionSchemaError, NoInvolvedError, InvolvedNotIterableError, TimestampTypeError, SchemaValidationError
from resources.groups import get_group, assert_access_to_group
from resources.login import get_user
from sqlalchemy.exc import IntegrityError, InterfaceError
from sqlalchemy.sql import func

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
    @jwt_required()
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
        output = dict()
        group = get_group(group_id)
        user = get_user(get_jwt_identity())
        assert_access_to_group(user.id, group.id)
        spent_per_participant = calculate_spent_per_participant(group)
        owes_per_participant = calculate_owes_per_participant(group)
        participants = list(set(spent_per_participant.keys()).union(owes_per_participant.keys()))
        participants.sort()
        for participant in participants:
            output[participant] = dict()
            output[participant]['spent'] = spent_per_participant[participant] if participant in spent_per_participant else 0
            output[participant]['owes'] = owes_per_participant[participant] if participant in owes_per_participant else 0
            output[participant]['credit'] = output[participant]['spent'] - output[participant]['owes']
            output[participant]['participant'] = participant
        return list(output.values())


def calculate_spent_per_participant(group):
    spent_as_tuple = db.session.query(
            Transaction.payer, func.sum(Transaction.amount).label('spent')
            ).filter_by(group_id=group.id).group_by(Transaction.payer).all()
    return {spent_tuple[0]:spent_tuple[1] for spent_tuple in spent_as_tuple}

def calculate_owes_per_participant(group):
    number_of_involved_per_transaction = db.session.query(
            Transaction.id, func.count(Involved.id).label('count')
            ).join(Transaction.involved).group_by(Transaction.id).subquery()
    owes_as_tuples = db.session.query(
            Involved.participant, 
            func.sum(Transaction.amount/number_of_involved_per_transaction.c.count).label('owes'),
            ).join(Transaction.involved).filter(Transaction.group_id==group.id).join(
                    number_of_involved_per_transaction, 
                    Transaction.id==number_of_involved_per_transaction.c.id
            ).group_by(Involved.participant).all()
    return {owes_tuple[0]:owes_tuple[1] for owes_tuple in owes_as_tuples}


# Get all participants of group
class Participants(Resource):
    @jwt_required()
    def get(self, group_id):
        group = get_group(group_id)
        user = get_user(get_jwt_identity())
        assert_access_to_group(user.id, group.id)
        participants = get_participants_of_group(group)
        response = {'participants': []}
        for p in participants:
            response['participants'].append(p[0])
        payers = Transaction.query.filter_by(group_id=group_id).with_entities(Transaction.payer).distinct()
        participants_set = set(response['participants'])
        for payer in payers:
            if payer[0] not in participants_set:
                response['participants'].append(payer[0])
        return response 

def get_participants_of_group(group):
        return Involved.query.join(Transaction).filter_by(group_id=group.id).with_entities(Involved.participant).distinct()


