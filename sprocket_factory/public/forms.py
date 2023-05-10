# -*- coding: utf-8 -*-
"""Public forms."""
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import DataRequired

from sprocket_factory.user.models import User

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        """Create instance."""
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, **kwargs):
        """Validate the form."""
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter_by(username=self.username.data).first()
        if not self.user:
            self.username.errors.append("Unknown username")
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append("Invalid password")
            return False

        if not self.user.active:
            self.username.errors.append("User not activated")
            return False
        return True

#Form used both for create and update a sprocket
class CreateSprocketForm(FlaskForm):
    id = IntegerField("Id", validators=[DataRequired()])
    teeth = IntegerField("Teeth", validators=[DataRequired()])
    pitch_diameter  = IntegerField("Pitch diameter", validators=[DataRequired()])
    outside_diameter  = IntegerField("Outside diameter", validators=[DataRequired()])
    pitch  = IntegerField("Pitch", validators=[DataRequired()])
    submit = SubmitField('Submit')