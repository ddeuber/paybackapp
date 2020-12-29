from flask import Flask
from unittest import TestCase
from api import app             # needs to be imported from api.py, otherwise endpoints are not defined
from database import db

class BaseCase(TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.db = db
    