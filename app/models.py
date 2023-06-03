from app import db, login_manager, app
from flask_login import UserMixin
import jwt
from datetime import datetime, timedelta, timezone

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(100), unique = True, nullable = False)
    password = db.Column(db.String(60), nullable = False)
    is_admin = db.Column(db.Boolean, nullable = False, default = False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.is_admin}')"
    
    def get_reset_token(self, expired_sec=1800):
        s = jwt.encode({"exp": datetime.now(tz=timezone.utc) + timedelta(
            seconds=expired_sec), "user_id": self.id}, app.config['SECRET_KEY'], algorithm="HS256")
        return s

    @staticmethod
    def verify_reset_token(token):
        try:
            s = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            user_id = s['user_id']
        except:
            return None
        return User.query.get(user_id)
    

class Camera(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), unique = True, nullable = False)
    update_date = db.Column(db.DateTime, nullable = False)
    description = db.Column(db.Text, nullable = False)
    video_src = db.Column(db.String(200), nullable = False)

    def __repr__(self):
        return f"Camera('{self.title}', '{self.update_date}')"