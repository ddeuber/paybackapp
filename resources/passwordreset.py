import flask
import datetime
from flask_restful import Resource 
from appconfig import app, mail
from database import db, User, hash_password
from flask_mail import Message
from threading import Thread
from resources.errors import SchemaValidationError, EmailDoesNotExistError, BadTokenError
from resources.login import get_user
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from jwt.exceptions import ExpiredSignatureError, DecodeError, InvalidTokenError


# Functions for sending mails asynchronously

def send_async_email(app, msg):
    with app.app_context():
            mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app, msg)).start()


### Endpoints

# ForgotPassword sends a mail to the the user's email address with a reset token needed for changing the password
class ForgotPassword(Resource):
    def post(self):
        body = flask.request.get_json(force=True)
        if not isinstance(body, dict):
            raise SchemaValidationError
        email = body.get('email')
        if email is None:
            raise SchemaValidationError
        user = User.query.filter_by(email=email).first()
        if not user:
            raise EmailDoesNotExistError
        reset_token = create_access_token(user.id, fresh=True)
        send_email('[PayApp] Reset Your Password',
                            sender='payappnoreply@gmail.com',
                            recipients=[user.email],
                            text_body=flask.render_template('reset_password.txt',
                                                    token=reset_token),
                            html_body=flask.render_template('reset_password.html',
                                                    token=reset_token))
        return {'message': 'Email for password reset will be sent shortly'}


# Reset password with access token 
class ResetPassword(Resource):
    @jwt_required(fresh=True)
    def post(self):
        body = flask.request.get_json(force=True)
        if not isinstance(body, dict):
            raise SchemaValidationError
        password = body.get('password')
        if password is None:
            raise SchemaValidationError
        user = get_user(get_jwt_identity())
        user.password = hash_password(password)
        db.session.commit()
        return {'message': 'Password successfully changed'}
