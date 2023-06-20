from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_admin import Admin
from flask_mail import Mail
from app.admin import MyAdminIndexView, BaseAdminView, UserAdminView
from app.config import Config


mail = Mail()
db = SQLAlchemy()
bcrypt = Bcrypt()

login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "info"

from app.models import User, Camera
# admin
admin = Admin(index_view=MyAdminIndexView())
admin.add_view(UserAdminView(User, db.session))
admin.add_view(BaseAdminView(Camera, db.session))


def create_app(config_class=Config):
    # app
    app = Flask(__name__)
    app.config.from_object(Config)

    # init
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    admin.init_app(app)

    # blueprints
    from app.users.routes import users
    from app.cameras.routes import cameras_bp
    from app.main.routes import main
    from app.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(cameras_bp)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
