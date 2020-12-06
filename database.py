from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from resources.errors import TimestampTypeError, InvalidEmailAddressError, SchemaValidationError, NoInvolvedError
import re

# Initialize database

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payapp_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


## Define tables

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(240), nullable=False)

    def __init__(self, user_dict):
        # Check if email string is valid
        if not re.match(r"[^@]+@[^@]+\.[^@]+", user_dict.get('email')):
            raise InvalidEmailAddressError
        self.email = user_dict.get('email')
        # TODO: hash password
        self.password = user_dict.get('password')


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)


class Groupaccess(db.Model):
    # This table determines which user has access to which groups.
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    user = db.relationship('User', backref='groupaccess')
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    group = db.relationship('Group', backref='groupaccess')
    deleted = db.Column(db.Boolean, nullable=False, default=False) # If True, the user no longer has access to the group


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator = db.Column(db.String(36), nullable=False)
    payer = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    comment = db.Column(db.String(80), nullable=False)
    creation_timestamp = db.Column(db.Integer, nullable=False)
    server_timestamp = db.Column(db.Integer, nullable=False, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    group = db.relationship('Group', backref='transactions')

    def __init__(self, transaction_dict, group):
            self.creator=transaction_dict.get('creator')
            self.payer=transaction_dict.get('payer')
            self.amount=transaction_dict.get('amount')
            self.comment=transaction_dict.get('comment')
            if not isinstance(transaction_dict.get('timestamp'), int):
                raise TimestampTypeError
            self.creation_timestamp=transaction_dict.get('timestamp')
            self.server_timestamp=int(datetime.now().timestamp()*1000)
            self.group = group 

    def to_dict(self):
        participants = []
        for involved_entry in self.involved:
            participants.append(involved_entry.participant)
        if len(participants) == 0:
            raise NoInvolvedError 
        return {
            #'id': self.id,
            'creator': self.creator,
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
    transaction = db.relationship('Transaction', backref="involved")



