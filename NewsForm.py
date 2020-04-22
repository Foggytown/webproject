# coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired

class NewsForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    categories = StringField('Категории')
    is_private = BooleanField("Личное")
    img_url = FileField('Картинка')
    submit = SubmitField('Применить')