from flask import Flask
from unittest import TestCase
from api import app             # needs to be imported from api.py, otherwise endpoints are not defined
import json
from database import db
import tempfile
import shutil
import os

# This function is used to create a temporary copy of the database
def create_temporary_copy(path):
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, 'temporary_database')
    shutil.copy2(path, temp_path)
    return temp_path


# Sets up app and temporary database
class BaseCase(TestCase):
    def setUp(self):
        self.dbpath = create_temporary_copy("test/test_database.db")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.dbpath
        self.app = app.test_client()
        self.db = db

    def tearDown(self):
        os.remove(self.dbpath)

    
# Logs in as user test@test.ch in order to obtain a valid token
class LoggedInBaseCase(BaseCase):
    def setUp(self):
        super().setUp()
        self.email = 'test@test.ch'
        body = json.dumps({'email': self.email, 'password': 'test'})
        response = self.app.post('/login', headers={'Content-Type': 'application/json'}, data=body)
        self.token = response.json['access_token']

    

