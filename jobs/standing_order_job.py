from croniter import croniter
from datetime import datetime
from database import db, StandingOrder, Transaction, Involved

def execute_standing_orders(logger):
    logger.info('Starting standing orders job.')
    standing_orders = StandingOrder.query.all()
    for standing_order in standing_orders:
        execute_standing_order(standing_order, logger)
    logger.info('Finished standing orders job.')


def execute_standing_order(standing_order, logger):
    logger.info('Check standing order' + str(standing_order.to_dict()))
    # Get the next execution date
    cron_iter = get_cron_iter(standing_order)
    now = datetime.now()
    if now >= cron_iter.get_next(datetime):
        logger.info('Add transaction for standing order' + str(standing_order.to_dict()))
        timestamp = int(now.timestamp()*1000)
        previous_last_execution = standing_order.last_execution
        standing_order.last_execution = timestamp

        # Generate transaction from standing order
        transaction = Transaction()
        transaction.fillWithStandingOrder(standing_order)
        db.session.add(transaction)

        if not standing_order.involved:
            raise NoInvolvedError
        for standing_order_involved in standing_order.involved: 
            involved = Involved(transaction=transaction, participant=standing_order_involved.participant)
            db.session.add(involved)

        db.session.commit()


def get_cron_iter(standing_order):
    last_execution = datetime.fromtimestamp(standing_order.get_last_execution_or_fallback()/1000)
    return croniter(standing_order.cron_expression, last_execution)
    
