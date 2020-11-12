from database import db, Transaction, Involved, Group


# Adds single transaction to database without commit.
def add_transaction(transaction):
    try:
        transaction_for_database = Transaction(transaction)
        db.session.add(transaction_for_database)
    except Exception as e:
        raise Exception('could not create transaction from your json')
    # Problem: at this point there is a transaction without involved
    at_least_one_participant = False
    for participant in transaction['involved']:
        at_least_one_participant = True
        involved = Involved(transaction=transaction_for_database, participant=participant)
        db.session.add(involved)
    if not at_least_one_participant:
        db.session.delete(transaction_for_database)
        raise Exception('there must be at least one participant involved')
