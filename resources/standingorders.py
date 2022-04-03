import flask
import time
import croniter
from flask_restful import Resource
from datetime import datetime
from database import db, StandingOrder, StandingOrderInvolved, Group, User
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt_identity
from resources.errors import NoInvolvedError, InvolvedNotIterableError, SchemaValidationError, EntityNotFoundError, EntityNotInGroupError
from resources.groups import get_group, assert_access_to_group
from resources.login import get_user
from sqlalchemy.exc import IntegrityError, InterfaceError
from jobs.standing_order_job import get_cron_iter

### Utility functions

# Adds a standing order to the database without commit
def add_standing_order(standing_order_dict, group, creator):
    standing_order = create_standing_order_from_dict(standing_order_dict)
    standing_order.group = group
    standing_order.creator = creator

    # Generate cron expression
    standing_order.periodicity = standing_order_dict.get('periodicity')
    if standing_order.periodicity == 'monthly':
        if isinstance(standing_order_dict.get('day'), int) and standing_order_dict.get('day') >= 0 and standing_order_dict.get('day') <= 28:
            standing_order.cron_expression = '0 0 {0} * *'.format(standing_order_dict.get('day'))
        elif standing_order_dict.get('day') is None:
            standing_order.cron_expression = '0 0 l * *'
        else:
            raise SchemaValidationError
    elif standing_order.periodicity == 'quarterly':
        standing_order.cron_expression = '0 0 1 */3 *'
    elif standing_order.periodicity ==  'yearly': 
        standing_order.cron_expression = '0 0 1 1 *'
    else:
        raise SchemaValidationError

    db.session.add(standing_order)

    # Add involved
    at_least_one_participant = False
    participants = standing_order_dict.get('involved')
    if not isinstance(participants, list):
        raise InvolvedNotIterableError 
    for participant in participants: 
        at_least_one_participant = True
        involved = StandingOrderInvolved(standing_order=standing_order, participant=participant)
        db.session.add(involved)
    if not at_least_one_participant:
        raise NoInvolvedError

    return standing_order.to_dict()


def create_standing_order_from_dict(standing_order_dict):
    if not isinstance(standing_order_dict, dict):
        raise SchemaValidationError
    standing_order = StandingOrder()
    standing_order.payer = standing_order_dict.get('payer')
    standing_order.amount = standing_order_dict.get('amount')
    standing_order.comment = standing_order_dict.get('comment')
    standing_order.creation_timestamp = int(time.time()*1000)
    return standing_order


### Resources 

class StandingOrders(Resource):
    # Add a standing order
    @jwt_required()
    def post(self, group_id):
        standing_order_dict = flask.request.get_json(force=True)
        group = get_group(group_id)
        user = get_user(get_jwt_identity())
        assert_access_to_group(user.id, group.id)
        try:
            standing_order =  add_standing_order(standing_order_dict, group, user)
            db.session.commit()
        except (IntegrityError, InterfaceError):
            raise SchemaValidationError 
        return standing_order, 201


    ## Get all standing orders
    @jwt_required()
    def get(self, group_id):
        group = get_group(group_id)
        user = get_user(get_jwt_identity())
        assert_access_to_group(user.id, group.id)

        standing_orders = []
        standing_order_query = StandingOrder.query.filter_by(group_id=group.id)
        now = datetime.now()
        for s in standing_order_query:
            standing_order_dict = s.to_dict()
            # Calculate next executions
            cron_iter = get_cron_iter(s)
            standing_order_dict['next_executions'] = []
            next_execution = now
            for i in range(3):
                next_execution = cron_iter.get_next(datetime)
                standing_order_dict['next_executions'].append(int(next_execution.timestamp()*1000))
            standing_orders.append(standing_order_dict)
        return standing_orders 


class DeleteStandingOrder(Resource):
    ## Delete a standing order
    @jwt_required()
    def delete(self, group_id, standing_order_id):
        standing_order = StandingOrder.query.get(standing_order_id)
        if standing_order is None:
            raise EntityNotFoundError
        if not standing_order.group_id == group_id:
            raise EntityNotInGroupError

        group = standing_order.group
        user = get_user(get_jwt_identity())
        assert_access_to_group(user.id, group.id)

        db.session.delete(standing_order)
        db.session.commit()
        return {'msg': 'successfully deleted standing order'}



