from flask_restful import Api
from appconfig import app
import sys
from resources.transactions import TransactionList, TransactionUpdate, AddTransaction, Debts, Participants
from resources.groups import AddGroup, GetGroupsForUser, AddUserToGroup, LeaveGroup
from resources.errors import errors
from resources.login import SignUp, Login, Refresh
from resources.passwordreset import ResetPassword, ForgotPassword
from resources.standingorders import StandingOrders, DeleteStandingOrder
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from jobs.standing_order_job import execute_standing_orders


api = Api(app, errors=errors)

#### Login endpoints
api.add_resource(SignUp, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Refresh, '/refresh')

#### Password Reset Endpoints
api.add_resource(ResetPassword, '/resetpassword')
api.add_resource(ForgotPassword, '/forgotpassword')

#### Transaction endpoints
api.add_resource(TransactionList, '/transactions/<int:group_id>')
api.add_resource(TransactionUpdate, '/update/<int:group_id>')
api.add_resource(AddTransaction, '/addtransaction/<int:group_id>')
api.add_resource(Debts, '/debts/<int:group_id>')
api.add_resource(Participants, '/participants/<int:group_id>')

#### Group endpoints   
api.add_resource(AddGroup, '/addgroup')
api.add_resource(GetGroupsForUser, '/groups')
api.add_resource(AddUserToGroup, '/addusertogroup/<int:group_id>')
api.add_resource(LeaveGroup, '/leavegroup/<int:group_id>')

#### Standing order endpoints
api.add_resource(StandingOrders, '/standingorders/<int:group_id>')
api.add_resource(DeleteStandingOrder, '/standingorders/<int:group_id>/<int:standing_order_id>')


if __name__ == '__main__':
    # Setup jobs
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=execute_standing_orders, trigger="interval", hours=1)
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

    # Run app 
    app.run(host='::', port=6000, debug=True)

