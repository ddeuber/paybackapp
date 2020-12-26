import flask
import flask_restful
from database import db, User
from resources.errors import SchemaValidationError, UnauthorizedError, InvalidLoginError
from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity
)

# Returns user by querying the database with user_id and throws an UnauthorizedError if the user is not part of the database.
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        raise UnauthorizedError
    return user
    

### Endpoints 

class SignUp(flask_restful.Resource):
    def post(self):
        user_dict = flask.request.get_json(force=True)
        user = User(user_dict)
        db.session.add(user)
        db.session.commit()
        return {'message': 'Successfully added user with email address ' + user.email}, 201


class Login(flask_restful.Resource):
    def post(self):
        user_dict = flask.request.get_json(force=True)
        if not isinstance(user_dict, dict):
            raise SchemaValidationError
        user = User.query.filter_by(email=user_dict.get('email')).first()
        if user is None:
            raise InvalidLoginError
        if user.check_password(user_dict.get('password')):
            return({'access_token': create_access_token(identity=user.id),
                    'refresh_token': create_refresh_token(identity=user.id)}), 200
        else:
            raise InvalidLoginError


class Refresh(flask_restful.Resource):
    @jwt_refresh_token_required
    def post(self):
        user_id = get_jwt_identity()
        return({'access_token': create_access_token(identity=user_id)}), 200
