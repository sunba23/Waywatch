from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt, mail
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestPasswordResetForm, ChooseNewPasswordForm
from app.models import User, Camera
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import os

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', cameras=cameras)

@app.route('/about')
def about():
    return render_template('about.html', title='About')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash(f'You are already logged in', category="info")
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created. Please log in.', category="success")
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash(f'You are already logged in', category="info")
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user= User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user=user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'You are now logged in', category="success")
            return redirect(next_page) if next_page else redirect(url_for('home'))
        flash(f'Login unsuccessful. Please check email and password', category="danger")
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash(f'You are now logged out', category="info")
    return redirect(url_for('home'))

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(f'Your account has been updated', category="success")
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('account.html', title='Account', form=form)

'''
@app.route('/cameras/<int:camera_id>')
@login_required
def camera(camera_id):
    camera = Camera.query.get_or_404(camera_id)
    return render_template('camera.html', title=camera.title, camera=camera)
'''

@app.route('/cameras')
@login_required
def cameras():
    cameras_ = Camera.query.all()
    return render_template('cameras.html', title='Cameras', cameras=cameras_)

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request",
                  sender=(os.environ.get('EMAIL_USER')),
                  recipients=[user.email])
    msg.body=f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this password reset request, please ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route('/reset_password', methods=['GET', 'POST'])
def request_reset():
    if current_user.is_authenticated:
        flash(f'You are already logged in', category="info")
        return redirect(url_for('home'))
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash(f'''Please check your email for instructions to reset your password. 
If you haven't received anything make sure to check the spam folder.''',
        category="info")
        return redirect(url_for('login'))
    return render_template('request_reset.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('This is an invalid or expired token.', category="warning")
        return redirect(url_for('request_reset'))
    form = ChooseNewPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash(f'Your password has been updated. Please log in.', category="success")
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)