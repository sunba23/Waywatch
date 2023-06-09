from app import db, login_manager
from flask_login import UserMixin
from flask import current_app
import jwt
from datetime import datetime, timedelta, timezone


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


favorites = db.Table('favorites',
                     db.Column('user_id',
                               db.Integer,
                               db.ForeignKey('user.id'),
                               primary_key=True),
                     db.Column('camera_id',
                               db.Integer,
                               db.ForeignKey('camera.id'),
                               primary_key=True))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    favorite_cameras = db.relationship('Camera',
                                       secondary=favorites,
                                       backref=db.backref('users',
                                                          lazy='dynamic'))
    is_premium = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.is_admin}', '{self.is_premium}')"

    def get_reset_token(self, expired_sec=1800):
        s = jwt.encode(
            {
                "exp": (datetime.now(tz=timezone.utc)
                        + timedelta(seconds=expired_sec)),
                "user_id": self.id
            },
            current_app.config['SECRET_KEY'],
            algorithm="HS256")
        return s

    @staticmethod
    def verify_reset_token(token):
        try:
            s = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=["HS256"]
                )
            user_id = s['user_id']
        except Exception:
            return None
        return User.query.get(user_id)


class Camera(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    video_src = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    is_premium = db.Column(db.Boolean, nullable=False, default=False)

    def get_embedded_video_src(self, video_src):
        video_id = video_src.split('=')[-1]
        embedded_src = f"https://www.youtube.com/embed/{video_id}"
        return embedded_src

    def __repr__(self):
        return (
            f'Camera("{self.title}", '
            f'"{self.description}", '
            f'"{self.video_src}", '
            f'"{self.latitude}", '
            f'"{self.longitude}")'
        )

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'video_src': self.video_src,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'is_premium': self.is_premium
        }
