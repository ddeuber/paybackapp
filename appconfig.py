import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from datetime import datetime
from dotenv import load_dotenv


# Initialize app
app = Flask(__name__)

# Load .env file for environment variables
# load_dotenv('.env.production')
# Alternative .env file for testing. This may fail if pipenv loads the .env file!
# load_dotenv('.env.test')
# load current env file
load_dotenv('.env')

# Import configuration from environment
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = bool(int(os.getenv('MAIL_USE_TLS'))) # booleans are encoded as 1 and 0
app.config['MAIL_USE_SSL'] = bool(int(os.getenv('MAIL_USE_SSL')))
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['PROPAGATE_EXCEPTIONS'] = bool(int(os.getenv('PROPAGATE_EXCEPTIONS')))


# Database configuration
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database, security and mail
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
mail = Mail(app)
