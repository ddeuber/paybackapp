from flask import Flask
from unittest import TestCase
from api import app             # needs to be imported from api.py, otherwise endpoints are not defined
import json
from database import db

class BaseCase(TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.db = db
    

class LoggedInBaseCase(BaseCase):
    def setUp(self):
        super().setUp()
        self.email = 'test@test.ch'
        body = json.dumps({'email': self.email, 'password': 'test'})
        response = self.app.post('/login', headers={'Content-Type': 'application/json'}, data=body)
        self.token = response.json['access_token']

