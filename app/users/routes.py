from flask import Blueprint
from flask_login import current_user, login_required
from app.models import Camera, User
from flask import render_template, url_for, flash, redirect, request
from app.users.forms import ChooseNewPasswordForm, RegistrationForm, LoginForm, RequestPasswordResetForm, UpdateAccountForm
from app import db, bcrypt
from flask_login import login_user, logout_user, current_user
from app.users.utils import send_reset_email

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash(f'You are already logged in', category="info")
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created. Please log in.', category="success")
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash(f'You are already logged in', category="info")
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user= User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user=user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'You are now logged in', category="success")
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        flash(f'Login unsuccessful. Please check email and password', category="danger")
    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    flash(f'You are now logged out', category="info")
    return redirect(url_for('main.home'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        favorite_cameras = Camera.query.filter(Camera.id.in_(form.favorite_cameras.data)).all()
        current_user.favorite_cameras = favorite_cameras
        db.session.commit()
        flash(f'Your account has been updated', category="success")
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.favorite_cameras.data = [camera.id for camera in current_user.favorite_cameras]
    
    return render_template(
        'account.html',
        title='Account',
        form=form,
        cameras=Camera.query.all() if current_user.is_premium
                            else Camera.query.filter_by(is_premium=False).all())


@users.route('/reset_password', methods=['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        flash(f'You are already logged in', category="info")
        return redirect(url_for('main.home'))
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(f'''Please check your email for instructions to reset your password. 
If you haven't received anything make sure to check the spam folder.''',
        category="info")
        return redirect(url_for('users.login'))
    return render_template('request_reset.html', title='Reset Password', form=form)


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('This is an invalid or expired token.', category="warning")
        return redirect(url_for('users.request_reset'))
    form = ChooseNewPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash(f'Your password has been updated. Please log in.', category="success")
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)