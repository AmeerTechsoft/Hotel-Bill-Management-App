from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, DateTimeField, SelectField, SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired
from datetime import datetime

class AddClientForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    contact_number = StringField('Contact Number', validators=[DataRequired()])
    email = StringField('Email')
    address = StringField('Address')
    submit = SubmitField('Add Client')

class CheckInForm(FlaskForm):
    room_id = SelectField('Room', validators=[DataRequired()])
    check_in = DateTimeField('Check-In Time', default=datetime.utcnow, format='%Y-%m-%d %H:%M:%S', validators=[DataRequired()])
    nights = IntegerField('Number of Nights', validators=[DataRequired()])
    submit = SubmitField('Check In')

class ServiceForm(FlaskForm):
    service_id = SelectField('Service', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Add Service')

class PaymentForm(FlaskForm):
    submit = SubmitField('Confirm Payment')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Enter your username"})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Enter your password"})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')