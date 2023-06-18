import os
from flask import url_for
from flask_mail import Message
from app import mail


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request",
                  sender=(os.environ.get('EMAIL_USER')),
                  recipients=[user.email])
    msg.body = ('To reset your password, visit the following link:'
                f'{url_for("users.reset_token", token=token, _external=True)}'
                'If you did not make this password reset request, '
                'please ignore this email and no changes will be made.'
    )
    mail.send(msg)
