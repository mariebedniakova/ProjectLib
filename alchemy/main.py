from flask import Flask, render_template, redirect
# noinspection PyUnresolvedReferences
from data.users import User
# noinspection PyUnresolvedReferences
from data.books import Book
# noinspection PyUnresolvedReferences
from data import db_session
from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField, StringField, IntegerField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from flask_login import LoginManager, login_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/library.db")


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    surname = StringField('Фамилия', nullable=True, default=None)
    name = StringField('Имя')
    age = IntegerField('Возраст', default=None)
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегестрироваться')


@app.route('/library/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        try:
            user = User(
                surname=form.surname.data,
                name=form.name.data,
                age=form.age.data,
                email=form.email.data,
                hashed_password=form.password.data)
            db_sess.add(user)
            db_sess.commit()
            return redirect("/library/successful_registration")
        except Exception:
            return render_template('registration.html',
                                   message="Недостаточно данных!",
                                   form=form)
    return render_template('registration.html', title='Регистрация', form=form)


@app.route('/library/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect("/library")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/library')
def index():
    pass
    # должна проверять, зарегестрирован ли пользователь и зависимо от этого выдавать html страницу


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
