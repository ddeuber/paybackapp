
from flask_restful import HTTPException

class NoInvolvedError(HTTPException):
    pass

class InvolvedNotIterableError(HTTPException):
    pass

class GroupNotFoundError(HTTPException):
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

class InvalidEmailAddressError(HTTPException):
    pass

class UnauthorizedError(HTTPException):
    pass

errors = {
    "NoInvolvedError": {
        "message": "There must be at least one participant involved",
        "status": 400
    },
    "InvolvedNotIterableError": {
        "message": "Involved must be a list",
        "status": 400
    },
    "GroupNotFoundError": {
        "message": "Group not found",
        "status": 400
    },
    "InvalidGroupNameError": {
        "message": "Group name is not valid",
        "status": 400
    },
    "TimestampTypeError": {
        "message": "Timestamp is not an integer",
        "status": 400
    },
    "TransactionSchemaError": {
        "message": "Error in transaction(s) JSON",
        "status" : 400
    },
    "InternalServerError": {
        "message": "Something went wrong",
        "status": 500
    },
    "SchemaValidationError": {
        "message": "JSON object is not correctly structured",
        "status": 400
    },
    "EmailAlreadyExistsError": {
        "message": "User with given email address already exists",
        "status": 400
    },
    "InvalidEmailAddressError": {
        "message": "Email address is not valid",
        "status": 400
    },
    "UnauthorizedError": {
        "message": "Invalid username or password",
        "status": 401
    }
}