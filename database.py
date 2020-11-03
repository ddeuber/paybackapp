from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize database

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


## Define tables

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator = db.Column(db.String(36), nullable=False)
    payer = db.Column(db.String(80), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    comment = db.Column(db.String(80), nullable=False)
    creation_timestamp = db.Column(db.Integer, nullable=False)
    server_timestamp = db.Column(db.DateTime, nullable=False, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    group = db.relationship('Group', backref='transactions')

class Involved(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'), nullable=False, index=True)
    transaction = db.relationship('Transaction', backref="involved")



