from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, ValidationError
from wtforms.validators import DataRequired


class TravelForm(FlaskForm):
    starting_point = StringField('Source', validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired()])
    myChoices = [
        ('DRIVING', 'Driving'),
        ('WALKING', 'Walking'),
        ('BICYCLING', 'Bicycling'),
        ('TRANSIT', 'Transit')
        ]
    commute_method = SelectField('Commute Method',
                                 choices=myChoices,
                                 validators=[DataRequired()])
    submit = SubmitField('Go')

    def validate_starting_point(self, field):
        if field.data == self.destination.data:
            raise ValidationError('Starting point and destination cannot be the same')

    def validate_destination(self, field):
        if field.data == self.starting_point.data:
            raise ValidationError('Starting point and destination cannot be the same')

        