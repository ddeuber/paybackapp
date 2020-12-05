#TODO:
# add authentication (maybe this can also include the group password)

import flask
import flask_restful
from flask_sqlalchemy import SQLAlchemy
from database import app, db, Transaction, Involved, Group, User
from datetime import datetime
from transaction_management import add_transaction
import json
import sys
from endpoints.transactions import TransactionList, TransactionUpdate, AddTransaction, Debts 
from endpoints.groups import AddGroup


api = flask_restful.Api(app)

#### Login endpoints

#### Transaction endpoints
api.add_resource(TransactionList, '/transactions/<string:group_name>')
api.add_resource(TransactionUpdate, '/update/<string:group_name>/<int:timestamp>')
api.add_resource(AddTransaction, '/add_transaction')
api.add_resource(Debts, '/debts/<string:group_name>')
#TODO: create endpoint to list participants of a group

#### Group endpoints   
api.add_resource(AddGroup, '/add_group')

if __name__ == '__main__':
    if len(sys.argv) == 3:
        tls_context = (sys.argv[1], sys.argv[2])
        app.run(host='::', debug=True, ssl_context=tls_context) 
    else:
        print('NOT USING HTTPS')
        print('use this command to enable HTTPS:')
        print('\t python3 app.py /path/to/cert /path/to/privkey')
        app.run(host='::', debug=True)
