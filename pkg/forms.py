from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, RadioField, DateField, SubmitField,SelectField
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, Regexp
)
from pkg.models import Banks 
from wtforms.validators import InputRequired, Email, Length
from wtforms import StringField, TextAreaField, SubmitField, HiddenField
from flask_wtf.file import FileField, FileAllowed

password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
password_validator = Regexp(regex=password_pattern, message='Invalid password format')

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()], render_kw={"placeholder": "Enter First Name"})
    last_name = StringField('Last Name', validators=[DataRequired()], render_kw={"placeholder": "Enter Last Name"})
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Enter Username"})
    email = StringField('Email', validators=[DataRequired(), Email()], render_kw={"placeholder": "Enter Email"})
    gender = RadioField('Gender', choices=[('male', 'Male'), ('female', 'Female')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[
        DataRequired(message='Please enter a password'),
        Length(min=8, message='Password must be at least 8 characters long'),
        password_validator
    ], render_kw={"placeholder": "Enter Password"})
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')], render_kw={"placeholder": "Confirm Password"})
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()], render_kw={"placeholder": "Enter Date of Birth"})
    next_of_kin = StringField('Next of Kin', validators=[DataRequired()], render_kw={"placeholder": "Enter Next of Kin"})
    phone = StringField('Phone', validators=[DataRequired()], render_kw={"placeholder": "Enter Phone"})
    address = StringField('Address', validators=[DataRequired()], render_kw={"placeholder": "Enter Address"})
    bank_account = StringField('Bank Account number', validators=[DataRequired()], render_kw={"placeholder": "Enter Bank Account Number"})
    bank_account_name = SelectField('Bank Name', choices=[], validators=[DataRequired()])
    submit = SubmitField('Submit')
    def set_bank_choices(self):
        # Fetch bank names from the database
        banks = Banks.query.all()

        # Populate choices for the SelectField
        self.bank_account_name.choices = [(bank.bank_id, bank.bank_name) for bank in banks]

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6)])
    submit = SubmitField('Login')

class QuestionForm(FlaskForm):
    question_id = HiddenField('Question ID')
    question_text = TextAreaField('Question Text', validators=[DataRequired()])
    option_a = StringField('Option A', validators=[DataRequired()])
    option_b = StringField('Option B', validators=[DataRequired()])
    option_c = StringField('Option C', validators=[DataRequired()])
    option_d = StringField('Option D', validators=[DataRequired()])
    correct_option = StringField('Correct Option (A, B, C, or D)', validators=[DataRequired()])
    file = FileField('Upload File', validators=[FileAllowed(['csv', 'sql', 'dump'], 'File type not allowed!')])

    submit = SubmitField('Submit')