from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    BooleanField,
    SubmitField,
    SelectField,
    RadioField
)
from wtforms.validators import DataRequired, NumberRange

class PasswordForm(FlaskForm):
    password_type = RadioField(
        'Password Type',
        choices=[('password', 'Random Password'), ('passphrase', 'Passphrase')],
        default='password'
    )
    strength_level = SelectField(
        'Strength Level',
        choices=[('1', 'Easy'), ('2', 'Medium'), ('3', 'Hard')],
        default='2'
    )
    length = IntegerField(
        'Length',
        validators=[DataRequired(), NumberRange(min=8, max=64)],
        default=12
    )
    use_digits = BooleanField('Include Digits', default=True)
    use_symbols = BooleanField('Include Symbols', default=True)
    submit = SubmitField('Generate Password')