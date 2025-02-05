from database import db
from appconfig import app

with app.app_context():
    db.create_all()