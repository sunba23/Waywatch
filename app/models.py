from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(100), unique = True, nullable = False)
    password = db.Column(db.String(60), nullable = False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"
    
class Camera(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(100), unique = True, nullable = False)
    update_date = db.Column(db.DateTime, nullable = False)
    description = db.Column(db.Text, nullable = False)
    video_src = db.Column(db.String(200), nullable = False)

    def __repr__(self):
        return f"Camera('{self.title}', '{self.update_date}')"