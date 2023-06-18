from flask import redirect, url_for, flash
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user


class BaseAdminView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        flash('You are not authorized to access this page.'
              'Please log in as an admin.',
              category='danger')
        return redirect(url_for('users.login'))


class UserAdminView(BaseAdminView):
    column_list = ['username', 'email', 'is_admin']


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You are not authorized to access this page. '
                  'Please log in as an admin first.',
                  category='danger')
            return redirect(url_for('users.login'))

        return super(MyAdminIndexView, self).index()
