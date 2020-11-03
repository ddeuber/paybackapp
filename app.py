#TODO:
# add authentication (maybe this can also include the group password)

import flask
import flask_restful
from flask_sqlalchemy import SQLAlchemy
from database import app, db, Transaction, Involved, Group
from datetime import datetime
import json

api = flask_restful.Api(app) 

class AddGroup(flask_restful.Resource):
    def post(self):
        group_from_request = flask.request.get_json(force=True)
        try:
            group_for_database = Group(group_from_request)
            db.session.add(group_for_database)
            db.session.commit()
            return {'id': group_for_database.id}, 201
        except Exception as e:
            if str(e).find('is not a string') != -1:
                return str(e), 400
            if str(e).find('UNIQUE constraint failed: group.name') != -1:
                return 'group name \'' + group_from_request['name'] + '\' already exists', 400
            return 'could not create group from your json', 400



# add a single transaction
class AddTransaction(flask_restful.Resource):
    def post(self):
        transaction_from_request = flask.request.get_json(force=True)
        try:
            transaction_for_database = Transaction(transaction_from_request)
            if Group.query.filter_by(id=transaction_for_database.group_id).first() is None:
                return 'group \'' + transaction_for_database.group_id + '\' does not exist', 400
            db.session.add(transaction_for_database)
            db.session.commit()
        except Exception as e:
            return 'could not create transaction from your json', 400
        # Problem: at this point there is a transaction without involved
        at_least_one_participant = False
        for participant in transaction_from_request['involved']:
            at_least_one_participant = True
            involved = Involved(transaction_id=transaction_for_database.id, participant=participant)
            db.session.add(involved)
        if not at_least_one_participant:
            db.session.delete(transaction_for_database)
            db.session.commit()
            return 'there must be at least one participant involved', 400
        db.session.commit()
        return {"added transaction": transaction_from_request}, 201

class TransactionList(flask_restful.Resource):
    def get(self, group_name):
        transactions = []
        try:
            group_id = Group.query.filter_by(name=group_name).first().id
        except:
            return 'could not find group \'' + group_name + '\'', 400
        for t in Transaction.query.filter_by(group_id=group_id):
            transactions.append(t.to_dict())
        return transactions

class Debts(flask_restful.Resource):
    def get(self, group_name):
        output = {}
        try:
            group_id = Group.query.filter_by(name=group_name).first().id
        except:
            return 'could not find group \'' + group_name + '\'', 400
        for t in Transaction.query.filter_by(group_id=group_id):
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



api.add_resource(TransactionList, '/transactions/<string:group_name>')
api.add_resource(AddGroup, '/add_group')
api.add_resource(AddTransaction, '/add_transaction')
api.add_resource(Debts, '/debts/<string:group_name>')

if __name__ == '__main__':
    app.run(host='::', debug=True)
