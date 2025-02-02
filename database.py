import re
from appconfig import db, bcrypt
from resources.errors import TimestampTypeError, InvalidEmailAddressError, SchemaValidationError, EmailAlreadyExistsError
from datetime import datetime


# Function for hashing passwords

def hash_password(password):
    return bcrypt.generate_password_hash(password)


###  Define tables

# Note that all timestamps are saved in milliseconds.

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(240), nullable=False)

    def __init__(self, user_dict):
        # Check if email string is valid
        if not isinstance(user_dict, dict):
            raise SchemaValidationError
        email = user_dict.get('email')
        if email is None:
            raise SchemaValidationError
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise InvalidEmailAddressError
        # Check if email already exists in database
        u = User.query.filter_by(email=email).first()
        if u is None:
            self.email = email
        else:
            raise EmailAlreadyExistsError
        # Check if password is nonempty and hash it
        password = user_dict.get('password')
        if password is None:
            raise SchemaValidationError
        self.password = hash_password(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class GroupAccess(db.Model):
    # This table determines which user has access to which groups.
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    user = db.relationship('User', backref='group_access_entries')
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    group = db.relationship('Group', backref='group_access_entries')


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payer = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    comment = db.Column(db.String(80), nullable=False)
    creation_timestamp = db.Column(db.Integer, nullable=False)
    server_timestamp = db.Column(db.Integer, nullable=False, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    group = db.relationship('Group', backref='transactions')
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', backref='transactions_created')

    def __init__(self, transaction_dict=None, group=None, creator=None):
        # empty constructor
        if transaction_dict is None or group is None or creator is None:
            return

        if not isinstance(transaction_dict, dict):
            raise SchemaValidationError
        self.payer=transaction_dict.get('payer')
        self.amount=transaction_dict.get('amount')
        self.comment=transaction_dict.get('comment')
        if not isinstance(transaction_dict.get('timestamp'), int):
            raise TimestampTypeError
        self.creation_timestamp = transaction_dict.get('timestamp')
        self.server_timestamp = int(datetime.now().timestamp()*1000)
        self.group = group 
        self.creator = creator

    # Create transaction from standing order. Note that the involved have to be added separately to the database.
    # Make sure to call this function after the last_execution has been updated to the current time as it will be used for the timestamps in the transaction.
    def fillWithStandingOrder(self, standing_order):
        self.payer = standing_order.payer
        self.amount = standing_order.amount
        self.comment = standing_order.comment
        self.creation_timestamp = standing_order.last_execution
        self.server_timestamp = standing_order.last_execution
        self.group_id = standing_order.group_id
        self.creator_id = standing_order.creator_id

    def to_dict(self):
        participants = []
        for involved_entry in self.involved:
            participants.append(involved_entry.participant)
        return {
            #'id': self.id,
            'creator': self.creator.email,
            'payer': self.payer,
            'amount': self.amount,
            'comment': self.comment,
            'timestamp': self.creation_timestamp,
            'involved': participants
        }


class Involved(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant = db.Column(db.String(80), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False, index=True)
    transaction = db.relationship('Transaction', backref='involved')


# StandingOrder with periodicity specified by cron_expression and last execution 
class StandingOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cron_expression = db.Column(db.String(80), nullable=False) 
    periodicity = db.Column(db.String(80), nullable=False)
    last_execution = db.Column(db.Integer, nullable=True)
    payer = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    comment = db.Column(db.String(80), nullable=False)
    creation_timestamp = db.Column(db.Integer, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    group = db.relationship('Group', backref='standing_orders')
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    creator = db.relationship('User', backref='standing_orders_created')

    def to_dict(self):
        participants = []
        for involved_entry in self.involved:
            participants.append(involved_entry.participant)
        return {
            'id': self.id,
            'creator': self.creator.email,
            'payer': self.payer,
            'amount': self.amount,
            'comment': self.comment,
            'timestamp': self.creation_timestamp,
            'involved': participants,
            'periodicity': self.periodicity,
            'last_execution_timestamp': self.last_execution
        }

    def get_last_execution_or_fallback(self):
        # Use creation_timestamp as a fallback if the standing order was not yet executed 
        if self.last_execution is None:
            return self.creation_timestamp
        return self.last_execution


class StandingOrderInvolved(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant = db.Column(db.String(80), nullable=False)
    standing_order_id = db.Column(db.Integer, db.ForeignKey('standing_order.id', ondelete='CASCADE'), nullable=False, index=True)
    standing_order = db.relationship('StandingOrder', backref=db.backref('involved', cascade='all,delete'))