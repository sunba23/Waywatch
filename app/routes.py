import re
from flask import render_template, url_for, flash, redirect, request, abort, Response
from app import app, db, bcrypt, mail
from app.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestPasswordResetForm, ChooseNewPasswordForm, TravelForm
from app.models import User, Camera
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import folium
import os
import numpy as np
import stripe


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/map')
def map():
    if current_user.is_authenticated:
        cameras = current_user.favorite_cameras
        m = folium.Map(location=[39.50, -98.35], zoom_start=4) # middle of mainland US

        for camera in cameras:
            link_url = url_for('camera', camera_id=camera.id)
            link_content = f'<a href="{link_url}" target="_blank">Camera {camera.title}</a>'
            popup = folium.Popup(link_content, max_width=300)
            folium.Marker([camera.latitude, camera.longitude], popup=popup).add_to(m)
        
        m = m._repr_html_()
        return render_template('map.html', map=m, title='Map')
    else:
        next_page = request.args.get('next')
        flash(f'You must be logged in to view this page', category="info")
        return redirect(url_for('login', next=next_page))

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
        favorite_cameras = Camera.query.filter(Camera.id.in_(form.favorite_cameras.data)).all()
        current_user.favorite_cameras = favorite_cameras
        db.session.commit()
        flash(f'Your account has been updated', category="success")
        return redirect(url_for('account'))
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


@app.route('/cameras/<int:camera_id>')
@login_required
def camera(camera_id):
    camera = Camera.query.get_or_404(camera_id)
    return render_template('camera.html', title=camera.title, camera=camera)


@app.route('/cameras')
@login_required
def cameras():
    user = current_user
    fav_cameras = user.favorite_cameras
    return render_template('cameras.html', title='Cameras', cameras=fav_cameras)


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


stripe.api_key = app.config['STRIPE_SECRET_KEY']

@app.route('/buy-premium', methods=['GET', 'POST'])
@login_required
def buy_premium():
    checkout_session = stripe.checkout.Session.create(
        payment_method_types = ['card'],
        line_items = [{
            'price': os.environ.get('STRIPE_PRICE_API_ID'),
            'quantity': 1,
            }],
        mode = 'payment',
        success_url = url_for('thanks', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url = url_for('home', _external=True)
    )
    
    return render_template(
        'buy_premium.html',
        title='Buy Premium', 
        checkout_session_id=checkout_session['id'], 
        checkout_public_key=app.config['STRIPE_PUBLIC_KEY'],
    )

@app.route('/thanks')
@login_required
def thanks():
    return render_template('thanks.html', title='Thank You!')


@app.route('/webhook', methods=['POST'])
def stripe_webhook():

    if request.content_length > 1024 * 1024:
        return abort(400)
    
    payload = request.get_data(as_text=True)
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = app.config['STRIPE_ENDPOINT_SECRET']
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError:
        return Response(status=400)
    except stripe.error.SignatureVerificationError:
        return Response(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)

    return Response(status=200)


@app.route('/travel', methods=['GET', 'POST'])
@login_required
def travel():
    if current_user.is_premium:
        form = TravelForm()
        maps_api_key = app.config['GOOGLE_MAPS_API']
        return render_template('travel.html', title='Travel', form=form, maps_api_key=maps_api_key, cameras=[camera.to_dict() for camera in Camera.query.all()])
    else:
        flash(f'You need to be a premium user to access this page.', category="warning")
        return redirect(url_for('home'))