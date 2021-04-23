from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, \
    SubmitField, StringField, IntegerField, TextField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    surname = StringField('Фамилия')
    name = StringField('Имя')
    age = IntegerField('Возраст')
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегестрироваться')


class OkForm(FlaskForm):
    submit = SubmitField('Перейти')


class BooksForm(FlaskForm):
    title = StringField('Название')
    author = StringField('Автор')
    year = IntegerField('Год написания')
    genre = StringField('Жанр')
    description = TextField('Описание')
    text = TextField('Текст')
    submit = SubmitField('Добавить')
