
from flask_restful import HTTPException

class NoInvolvedError(HTTPException):
    pass

class InvolvedNotIterableError(HTTPException):
    pass

class GroupNotFoundError(HTTPException):
    pass

class NoAccessToGroupError(HTTPException):
    pass

class UserNotFoundError(HTTPException):
    pass

class UserAlreadyInGroup(HTTPException):
    pass

class InvalidGroupNameError(HTTPException):
    pass 

class TimestampTypeError(HTTPException):
    pass

class TransactionSchemaError(HTTPException):
    pass

class InternalServerError(HTTPException):
    pass

class SchemaValidationError(HTTPException):
    pass

class EmailAlreadyExistsError(HTTPException):
    pass

class EmailDoesNotExistError(HTTPException):
    pass

class InvalidEmailAddressError(HTTPException):
    pass

class UnauthorizedError(HTTPException):
    pass

class InvalidLoginError(HTTPException):
    pass

class BadTokenError(HTTPException):
    pass

class EntityNotFoundError(HTTPException):
    pass

class EntityNotInGroupError(HTTPException):
    pass

errors = {
    'NoInvolvedError': {
        'message': 'There must be at least one participant involved',
        'status': 400
    },
    'InvolvedNotIterableError': {
        'message': 'Involved must be a list',
        'status': 400
    },
    'GroupNotFoundError': {
        'message': 'Group not found',
        'status': 400
    },
    'NoAccessToGroupError': {
        'message': 'User is not authorized to access group',
        'status': 403
    },
    'UserNotFoundError': {
        'message': 'User not found',
        'status': 400
    },
    'UserAlreadyInGroup': {
        'message': 'User has already access to group',
        'status': 400
    },
    'InvalidGroupNameError': {
        'message': 'Group name is not valid',
        'status': 400
    },
    'TimestampTypeError': {
        'message': 'Timestamp is not an integer',
        'status': 400
    },
    'TransactionSchemaError': {
        'message': 'Error in transaction(s) JSON',
        'status' : 400
    },
    'InternalServerError': {
        'message': 'Something went wrong',
        'status': 500
    },
    'SchemaValidationError': {
        'message': 'JSON object is not correctly structured',
        'status': 400
    },
    'EmailAlreadyExistsError': {
        'message': 'User with given email address already exists',
        'status': 400
    },
    'EmailDoesNotExistError': {
        'message': 'User with given email address does not exist',
        'status': 400
    },
    'InvalidEmailAddressError': {
        'message': 'Email address is not valid',
        'status': 400
    },
    'UnauthorizedError': {
        'message': 'Not authorized',
        'status': 401
    },
    'InvalidLoginError': {
        'message': 'Invalid username or password',
        'status': 401
    },
    'BadTokenError': {
        'message': 'Invalid token',
        'status': 403
    },
    'EntityNotFoundError': {
        'message': 'Entity not found',
        'status': 400
    },
    'EntityNotInGroupError': {
        'message': 'Entity not found in this group',
        'status': 400
    }
}