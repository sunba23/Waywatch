from flask import Flask, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = '2f03ef2cc69979cbad9d947ceaee4e84'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


class BaseAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash('You are not authorized to access this page. Please log in as an admin.', category='danger')
        return redirect(url_for('login'))
    
class UserAdminView(BaseAdminView):
    column_list = ['username', 'email', 'is_admin']

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You are not authorized to access this page. Please log in as an admin first.', category='danger')
            return redirect(url_for('login'))
        
        return super(MyAdminIndexView, self).index()

from app.models import User, Camera
admin = Admin(app, index_view=MyAdminIndexView())
admin.add_view(UserAdminView(User, db.session))
admin.add_view(BaseAdminView(Camera, db.session))

from app import routes