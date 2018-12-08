# _*_ coding: utf-8 _*_

from flask_security import current_user
from flask_security.forms import (
    RegisterForm, LoginForm, SendConfirmationForm,
    StringField, PasswordField,
    Length, Required, EqualTo, email_required, password_required,
    ValidationError, email_validator, valid_user_email,
    _datastore, get_message,
)
from flask_security.utils import verify_and_update_password


name_required = Required(message='No name has been input.')
name_length = Length(min=3, max=20, message='Length should be between 3 - 20.')


def valid_user_email_for_oauth(form, field):
    if not field.data:
        return
    form.user = _datastore.get_user(field.data)
    if form.user is None:
        raise ValidationError(get_message('USER_NOT_EXISTS')[0])


def unique_user_name(form, field):
    if _datastore.get_user_name(field.data) is not None:
        msg = f'{field.data} has already been used.'
        raise ValidationError
    if '@' in field.data:
        raise ValidationError('Special symbols not allowed in username.')


def unique_email(form, field):
    if form.origin_email.data == field.data:
        raise ValidationError(('Please use a different email from the current one.'))


def unique_user_email(form, field):
    if _datastore.get_user_email(field.data) is not None:
        msg = get_message('EMAIL_ALREADY_ASSOCIATED', email=field.data)[0]
        raise ValidationError(msg)


class ExtendedLoginForm(LoginForm):
    email = StringField('Email/Username',
                        validators=[Required(message='No account info has been input.')])
    password = PasswordField('Password',
                             validators=[password_required])


class ExtendedRegisterForm(RegisterForm):
    name = StringField('Username', validators=[name_required, name_length,
                                               unique_user_name])
    email = StringField('Email', validators=[email_required, email_validator,
                                             unique_user_email])
    password = PasswordField('Password', validators=[password_required])
    password_confirm = PasswordField('Retype Password',
                                     validators=[EqualTo('password', message='RETYPE_PASSWORD_MISMATCH'),
                                                 password_required])


class ResetEmailForm(SendConfirmationForm):
    origin_email = StringField('Current Email(ReadOnly)', render_kw={'readonly': True},
                               validators=[email_required, email_validator, valid_user_email])
    email = StringField('New Email', validators=[email_required, email_validator,
                                                 unique_user_email, unique_email])
    password = PasswordField('Password', validators=[password_required])

    def validate(self):
        if not super(SendConfirmationForm, self).validate():
            return False
        if not verify_and_update_password(self.password.data, current_user):
            self.password.errors.append('Invalid password')
            return False
        return True


class ResetEmailForOauthForm(SendConfirmationForm):
    origin_email = StringField('Current Email(ReadOnly', render_kw={'readonly': True},
                          validators=[valid_user_email_for_oauth])
    email = StringField('New Email', validators=[email_required, email_validator,
                                                 unique_user_email, unique_email])
    password = PasswordField('Password(optional)')
