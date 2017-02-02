
from flask_wtf import Form
from wtforms import (
    StringField,
    IntegerField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    IPAddress,
    NumberRange
)


class JoinForm(Form):
    ip = StringField('IP', default='127.0.0.1', validators=[DataRequired(), IPAddress()])
    port = IntegerField('Port', validators=[DataRequired(), NumberRange(min=1, max=65535)])
    join = SubmitField('Join')
