import flask
import flask_restful
from transaction_management import add_transaction
from database import db, Transaction, Involved, Group, User




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
            group = Group.query.filter_by(name=group_name).first()
            if group is None:
                raise Exception('could not find group \'' + group_name + '\'')
            return_transaction_list = [t.to_dict() for t in Transaction.query.join(Group).filter(Group.id==group.id).filter(Transaction.server_timestamp>timestamp)]

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