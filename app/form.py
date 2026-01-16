from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField
from wtforms.validators import Email, DataRequired

class SignUp(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("confirm_password", validators=[DataRequired()])
    button = SubmitField("Sign ip")

class SignIn(FlaskForm):
    email = EmailField("Email", validators=[Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    button = SubmitField("Sign in")

class CreateTask(FlaskForm):
    task = StringField("Task", validators=[DataRequired()])
    button = SubmitField("Create")
