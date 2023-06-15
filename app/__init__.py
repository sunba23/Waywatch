from flask import Flask, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask_mail import Mail
import stripe


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = '2f03ef2cc69979cbad9d947ceaee4e84'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS']  = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')  
app.config['STRIPE_PUBLIC_KEY'] = os.environ.get('STRIPE_PUBLIC_KEY')
app.config['STRIPE_SECRET_KEY'] = os.environ.get('STRIPE_SECRET_KEY')
app.config['STRIPE_PRICE_API_ID'] = os.environ.get('STRIPE_PRICE_API_ID')
app.config['STRIPE_ENDPOINT_SECRET'] = os.environ.get('STRIPE_ENDPOINT_SECRET')

stripe.api_key = app.config['STRIPE_SECRET_KEY']
mail = Mail(app)
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