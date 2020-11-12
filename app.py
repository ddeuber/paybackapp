#TODO:
# add authentication (maybe this can also include the group password)

import flask
import flask_restful
from flask_sqlalchemy import SQLAlchemy
from database import app, db, Transaction, Involved, Group
from datetime import datetime
from transaction_management import add_transaction
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
                return {'error': str(e)}, 400
            if str(e).find('UNIQUE constraint failed: group.name') != -1:
                return {'error': 'group name \'' + group_from_request['name'] + '\' already exists'}, 400
            return {'error': 'could not create group from your json'}, 400



# add a single transaction
class AddTransaction(flask_restful.Resource):
    def post(self):
        transaction_from_request = flask.request.get_json(force=True)
        try:
            add_transaction(transaction_from_request)
        except Exception as e:
            return {'error': str(e)}, 400
        # Problem: at this point there is a transaction without involved
        db.session.commit()
        return {'added transaction': transaction_from_request}, 201

class TransactionList(flask_restful.Resource):
    def get(self, group_name):
        transactions = []
        try:
            group_id = Group.query.filter_by(name=group_name).first().id
        except:
            return {'error': 'could not find group \'' + group_name + '\''}, 400
        for t in Transaction.query.filter_by(group_id=group_id):
            transactions.append(t.to_dict())
        return transactions

# Upload new transactions and download transaction uploaded after timestamp
class TransactionUpdate(flask_restful.Resource):
    def post(self, group_name, timestamp):
        request_transaction_list= flask.request.get_json(force=True)
        try:
            ## Get transactions added after timestamp
            try:
                group = Group.query.filter_by(name=group_name).first()
                return_transaction_list =  group.transactions.filter_by(server_timestamp > timestamp)
            except:
                raise Exception('could not find group \'' + group_name + '\''})
            ## Add new transactions
            for transaction in request_transaction_list:
                add_transaction(transaction)
            db.session.commit()
            return {"server_timestamp": int(datetime.now().timestamp()*1000), "transactions": return_transaction_list}
        except Exception as e:
            return {'error': str(e)}, 400


class Debts(flask_restful.Resource):
    def get(self, group_name):
        output = {}
        try:
            group_id = Group.query.filter_by(name=group_name).first().id
        except:
            return {'error': 'could not find group \'' + group_name + '\''}, 400
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
api.add_resource(TransactionUpdate, '/update/<string:group_name>/<int:timestamp>')
api.add_resource(AddGroup, '/add_group')
api.add_resource(AddTransaction, '/add_transaction')
api.add_resource(Debts, '/debts/<string:group_name>')

if __name__ == '__main__':
    app.run(host='::', debug=True)
