from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize database

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payapp_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


## Define tables

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    def __init__(self, group_dict):
        if not isinstance(group_dict['name'], str):
            raise Exception('name is not a string')
        if not isinstance(group_dict['password'], str):
            raise Exception('password is not a string')
        self.name = group_dict['name']
        self.password = group_dict['password']

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

    def __init__(self, transaction_dict):
        self.creator=transaction_dict['creator']
        self.payer=transaction_dict['payer']
        self.amount=transaction_dict['amount']
        self.comment=transaction_dict['comment']
        self.creation_timestamp=transaction_dict['timestamp']
        self.server_timestamp=int(datetime.now().timestamp()*1000)
        self.group = Group.query.filter_by(name=transaction_dict['group_name']).first()

    def to_dict(self):
        participants = []
        for involved_entry in Involved.query.filter_by(transaction_id=self.id):
            participants.append(involved_entry.participant)
        if len(participants) == 0:
            raise Exception('no one is involved in transaction with id ' + str(self.id))
        return {
            #'id': self.id,
            'creator': self.creator,
            'payer': self.payer,
            'amount': self.amount,
            'comment': self.comment,
            'timestamp': self.creation_timestamp,
            'group_name': self.group.name,
            'involved': participants
        }

class Involved(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant = db.Column(db.String(80), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False, index=True)
    transaction = db.relationship('Transaction', backref="involved")



