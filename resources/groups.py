import flask
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from database import db, Transaction, Involved, Group, User, GroupAccess
from resources.errors import InvalidGroupNameError, SchemaValidationError, NoAccessToGroupError, GroupNotFoundError, UserNotFoundError, UserAlreadyInGroup
from resources.login import get_user
from sqlalchemy.exc import IntegrityError, InterfaceError


# Returns group by querying the database with group_id and throws an erro rif the group is not part of the database.
def get_group(group_id):
    group = Group.query.get(group_id)
    if group is None:
        raise GroupNotFoundError
    return group

# Raises UnauthorizedError if user does not have access to group
def assert_access_to_group(user_id, group_id):
    group_access = GroupAccess.query.filter_by(user_id=user_id, group_id=group_id).first()
    if group_access is None:
        raise NoAccessToGroupError 
    return group_access


### Endpoints

class AddGroup(Resource):
    @jwt_required
    def post(self):
        user = get_user(get_jwt_identity())
        group_from_request = flask.request.get_json(force=True)
        if not isinstance(group_from_request, dict):
            raise SchemaValidationError
        try:
            group_for_database = Group(name=group_from_request.get('name'))
            db.session.add(group_for_database)
            group_access = GroupAccess(user=user, group=group_for_database)
            db.session.add(group_access)
            db.session.commit()
            return {'id': group_for_database.id}, 201
        except (IntegrityError, InterfaceError): 
            raise InvalidGroupNameError


# Returns the list of groups where the user is a member
class GetGroupsForUser(Resource):
     @jwt_required
     def get(self):
        user = get_user(get_jwt_identity())
        groups = []
        for group_access in user.group_access_entries:
            groups.append(group_access.group.to_dict())
        return { "groups": groups }


# Add another member to group by his email
class AddUserToGroup(Resource):
    @jwt_required
    def post(self, group_id):
        # First check if user and group exist
        user = get_user(get_jwt_identity())
        group = get_group(group_id) 
        # Check that user has access to the group
        assert_access_to_group(user.id, group.id)
        # Get new member from request
        body = flask.request.get_json(force=True)
        if not isinstance(body, dict):
            raise SchemaValidationError
        new_member = User.query.filter_by(email=body.get('email')).first()
        if new_member is None:
            raise UserNotFoundError
        # Return error if new_member is already part of group
        has_group_access = GroupAccess.query.filter_by(user_id=new_member.id, group_id=group.id).first()
        if has_group_access is not None:
            raise UserAlreadyInGroup
        # Add new_member to group
        group_access = GroupAccess(user=new_member, group=group)
        db.session.add(group_access)
        db.session.commit()
        return {'message': 'Successfully added new member to group'}, 200


class LeaveGroup(Resource):
    @jwt_required
    def post(self, group_id):
        # First check if user and group exist
        user = get_user(get_jwt_identity())
        group = get_group(group_id) 
        group_access = assert_access_to_group(user.id, group.id)        
        # Remove group access from database
        db.session.delete(group_access)
        db.session.commit()
        return {'message': 'Successfully removed user from group'}, 200
