import flask
import flask_restful
from database import db, Transaction, Involved, Group, User

class AddGroup(flask_restful.Resource):
    def post(self):
        group_from_request = flask.request.get_json(force=True)
        try:
            group_for_database = Group(group_from_request)
            db.session.add(group_for_database)
            db.session.commit()
            return {'id': group_for_database.id}, 201
        except Exception as e:
            print(str(e))
            if str(e).find('is not a string') != -1:
                return {'error': str(e)}, 400
            if str(e).find('UNIQUE constraint failed: group.name') != -1:
                return {'error': 'group name \'' + group_from_request['name'] + '\' already exists'}, 400
            return {'error': 'could not create group from your json'}, 400
