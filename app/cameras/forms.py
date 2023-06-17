from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class TravelForm(FlaskForm):
    starting_point = StringField('Source', validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired()])
    myChoices = [
        ('driving', 'Driving'),
        ('walking', 'Walking'),
        ('bicycling', 'Bicycling')
        ]
    commute_method = SelectField('Commute Method',
                                choices=myChoices,
                                validators=[DataRequired()]
                                )
    submit = SubmitField('Go')