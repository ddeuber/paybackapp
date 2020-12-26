#TODO:
# add authentication (maybe this can also include the group password)

import flask_restful
from database import app, db
import sys
from resources.transactions import TransactionList, TransactionUpdate, AddTransaction, Debts 
from resources.groups import AddGroup, GetGroupsForUser, AddUserToGroup, LeaveGroup
from resources.errors import errors
from resources.login import SignUp, Login, Refresh


api = flask_restful.Api(app, errors=errors)

#### Login endpoints
api.add_resource(SignUp, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Refresh, '/refresh')

#### Transaction endpoints
api.add_resource(TransactionList, '/transactions/<int:group_id>')
api.add_resource(TransactionUpdate, '/update/<int:group_id>')
api.add_resource(AddTransaction, '/addtransaction/<int:group_id>')
api.add_resource(Debts, '/debts/<int:group_id>')

#### Group endpoints   
api.add_resource(AddGroup, '/addgroup')
api.add_resource(GetGroupsForUser, '/groups')
api.add_resource(AddUserToGroup, '/addusertogroup/<int:group_id>')
api.add_resource(LeaveGroup, '/leavegroup/<int:group_id>')

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
