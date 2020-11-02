from flask import Flask
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from database import app, db  

api = Api(app) 

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)