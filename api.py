#TODO:
# add authentication (maybe this can also include the group password)

import flask_restful
from database import app, db
import sys
from resources.transactions import TransactionList, TransactionUpdate, AddTransaction, Debts 
from resources.groups import AddGroup
from resources.errors import errors


api = flask_restful.Api(app, errors=errors)

#### Login endpoints

#### Transaction endpoints
api.add_resource(TransactionList, '/transactions/<int:group_id>')
api.add_resource(TransactionUpdate, '/update/<int:group_id>')
api.add_resource(AddTransaction, '/add_transaction/<int:group_id>')
api.add_resource(Debts, '/debts/<int:group_id>')

#### Group endpoints   
api.add_resource(AddGroup, '/add_group')
#TODO: create endpoint to list participants of a group

if __name__ == '__main__':
    if len(sys.argv) == 3:
        tls_context = (sys.argv[1], sys.argv[2])
        app.run(host='::', debug=True, ssl_context=tls_context) 
    else:
        print('NOT USING HTTPS')
        print('use this command to enable HTTPS:')
        print('\t python3 api.py /path/to/cert /path/to/privkey')
        app.run(host='::', debug=True)
