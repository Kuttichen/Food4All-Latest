from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField,RadioField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange, Optional
from flaskblog.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Institution / Hotel Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    usertype = RadioField('Select User Type',choices=[('Consumer','Consumer'),('Vendor','Vendor')])

    location = StringField('Location',
                           validators=[DataRequired(), Length(min=2, max=15)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    location = StringField('Location',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class PostForm1(FlaskForm):
    food = StringField('Available Food',validators=[DataRequired()])
    people = IntegerField('Available Quantity',validators=[DataRequired(), NumberRange(min=1,max=100,message='Enter a number between 1 & 100')] )
    submit = SubmitField('Post')

class PostForm2(FlaskForm):
    people = IntegerField('Required Quantity ',validators=[DataRequired(),NumberRange(min=1,max=100,message='Enter a number between 1 &100')] )
    food = StringField('Preferred Food')
    submit = SubmitField('Post')