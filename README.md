
# Waywatch


This is a flask app in which users can browse, watch live cameras and select their favorites. After paying for a premium account, you can plan a trip using different commute methods, and see only the relevant cameras for the planned trip.


## Pre-requirements

To run this project, please first set up the given environment variables:

SECRET_KEY - can be anything, used for hashing.\
EMAIL_USER, EMAIL_PASS - those will be used for the account sending confirmation mails etc. Must be a real account.\
STRIPE_PUBLIC_KEY, STRIPE_SECRET_KEY - [found on stripe](https://docs.stripe.com/keys) \
STRIPE_ENDPOINT_SECRET - [found on stripe](https://docs.stripe.com/webhooks) \
STRIPE_PRICE_API_ID - found on stripe, after creating a product\
GOOGLE_MAPS_API_2 - [google maps API key](https://developers.google.com/maps/documentation/javascript/get-api-key)


And set up the database with sqlalchemy ORM using [models.py](https://github.com/sunba23/Waywatch/blob/master/app/models.py).


## Usage

Create and activate a virtual environment, after that run
```bash
pip3 install -r requirements.txt
python3 run.py
```
