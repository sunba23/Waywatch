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

    def validate_starting_point(self, starting_point):
        if starting_point.data == self.destination.data:
            raise ValidationError(
                'Starting point and destination cannot be the same')

    def validate_destination(self, destination):
        if destination.data == self.starting_point.data:
            print('error was raised')
            raise ValidationError(
                'Starting point and destination cannot be the same')
