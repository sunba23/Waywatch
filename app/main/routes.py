from flask import (Response, abort, render_template,
                   request, Blueprint, url_for, current_app)
from flask_login import login_required, current_user
import os
import stripe
from app import db
from app.models import User

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    return render_template('home.html')


@main.route('/about')
def about():
    return render_template('about.html', title='About')


@main.route('/buy-premium', methods=['GET', 'POST'])
@login_required
def buy_premium():
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': os.environ.get('STRIPE_PRICE_API_ID'),
            'quantity': 1,
            }],
        mode='payment',
        success_url=(url_for('main.thanks', _external=True)
                     + '?session_id={CHECKOUT_SESSION_ID}'),
        cancel_url=url_for('main.home', _external=True)
    )

    return render_template(
        'buy_premium.html',
        title='Buy Premium',
        checkout_session_id=checkout_session['id'],
        checkout_public_key=current_app.config['STRIPE_PUBLIC_KEY'],
    )


@main.route('/thanks')
@login_required
def thanks():
    session_id = request.args.get('session_id')
    if session_id:
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
        session = stripe.checkout.Session.retrieve(session_id)
        if session and session.payment_status == 'paid':
            user = User.query.get(current_user.id)
            user.is_premium = True
            db.session.commit()
            return render_template('thanks.html', title='Thank You!')
    return abort(400)


@main.route('/webhook', methods=['POST'])
def stripe_webhook():

    if request.content_length > 1024 * 1024:
        return abort(400)

    payload = request.get_data(as_text=True)
    sig_header = request.environ.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = current_app.config['STRIPE_ENDPOINT_SECRET']
    event = None

    try:
        event = stripe.Webhook.construct_event(payload,
                                               sig_header,
                                               endpoint_secret)
    except ValueError:
        return Response(status=400)
    except stripe.error.SignatureVerificationError:
        return Response(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print(session)

    return Response(status=200)
