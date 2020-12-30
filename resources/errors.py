
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

errors = {
    'NoInvolvedError': {
        'msg': 'There must be at least one participant involved',
        'status': 400
    },
    'InvolvedNotIterableError': {
        'msg': 'Involved must be a list',
        'status': 400
    },
    'GroupNotFoundError': {
        'msg': 'Group not found',
        'status': 400
    },
    'NoAccessToGroupError': {
        'msg': 'User is not authorized to access group',
        'status': 403
    },
    'UserNotFoundError': {
        'msg': 'User not found',
        'status': 400
    },
    'UserAlreadyInGroup': {
        'msg': 'User has already access to group',
        'status': 400
    },
    'InvalidGroupNameError': {
        'msg': 'Group name is not valid',
        'status': 400
    },
    'TimestampTypeError': {
        'msg': 'Timestamp is not an integer',
        'status': 400
    },
    'TransactionSchemaError': {
        'msg': 'Error in transaction(s) JSON',
        'status' : 400
    },
    'InternalServerError': {
        'msg': 'Something went wrong',
        'status': 500
    },
    'SchemaValidationError': {
        'msg': 'JSON object is not correctly structured',
        'status': 400
    },
    'EmailAlreadyExistsError': {
        'msg': 'User with given email address already exists',
        'status': 400
    },
    'EmailDoesNotExistError': {
        'msg': 'User with given email address does not exist',
        'status': 400
    },
    'InvalidEmailAddressError': {
        'msg': 'Email address is not valid',
        'status': 400
    },
    'UnauthorizedError': {
        'msg': 'Not authorized',
        'status': 401
    },
    'InvalidLoginError': {
        'msg': 'Invalid username or password',
        'status': 401
    },
    'BadTokenError': {
        'msg': 'Invalid token',
        'status': 403
    }
}