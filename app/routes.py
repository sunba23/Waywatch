from flask import render_template, url_for, flash, redirect
from app import app
from app.forms import RegistrationForm, LoginForm
from app.models import User, Camera

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
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data} successfully', category="success")
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'You are now logged in', category="success")
        return redirect(url_for('home'))
    return render_template('login.html', title='Login', form=form)