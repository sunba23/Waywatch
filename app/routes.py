from flask import render_template, url_for, flash, redirect, request
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm
from app.models import User, Camera
from flask_login import login_user, current_user, logout_user, login_required

cameras = [
    {
        'id': 1,
        'title': 'here goes street name 1',
        'update_date': 'here goes the last update timestamp',
        'description': 'here goes description',
        'video_src': 'here goes camera image from cv2'
    },
    {
        'id': 2,
        'title': 'here goes street name 2',
        'update_date': 'here goes the last update timestamp',
        'description': 'here goes description',
        'video_src': 'here goes camera image from cv2'
    }
]

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

@app.route('/account')
@login_required
def account():
    return render_template('account.html', title='Account')