import flask
import flask_restful
from database import db, Transaction, Involved, Group, User
from resources.errors import InvalidGroupNameError, SchemaValidationError
from sqlalchemy.exc import IntegrityError, InterfaceError

class AddGroup(flask_restful.Resource):
    def post(self):
        group_from_request = flask.request.get_json(force=True)
        if not isinstance(group_from_request, dict):
            raise SchemaValidationError
        try:
            group_for_database = Group(name=group_from_request.get('name'))
            db.session.add(group_for_database)
            db.session.commit()
            return {'id': group_for_database.id}, 201
        except (IntegrityError, InterfaceError): 
            raise InvalidGroupNameError
