from flask import Flask, render_template, redirect
# noinspection PyUnresolvedReferences
from data.users import User
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
# Словарь, хранящий предыдущую страницу по ключу email пользователя в виде словаря
# с ключами "url" и "title" (см. login())
# Нужен, чтобы после регистрации и авторизации пользователь,
# которому Алиса рекомендовала книгу, мог вернуться на страницу этой книги
previous_pages = {}

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
    surname = StringField('Фамилия', default=None)
    name = StringField('Имя')
    age = IntegerField('Возраст')
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегестрироваться')


class OkForm(FlaskForm):
    submit = SubmitField('Перейти')


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
    return render_template('registration.html', title='Регистрация', form=form,
                           description='Регистрация в электронной библиотеке')


@app.route('/library/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            if user.email not in previous_pages:
                previous_pages[user.email] = {}
                previous_pages[user.email]['url'] = f'/{user.email}'
                previous_pages[user.email]['title'] = f'{user.name} {user.surname}'
            return redirect("/library" + previous_pages[user.email]['url'])
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/library/<user_email>')
def index(user_email):
    return render_template('home_page.html', title=previous_pages[user_email]['title'],
                           description='Электронная библиотека')

    # должна проверять, зарегестрирован ли пользователь и зависимо от этого выдавать html страницу


@app.route('/library/successful_registration', methods=['GET', 'POST'])
def successful_registration():
    form = OkForm()
    if form.validate_on_submit():
        return redirect('/library/login')
    return render_template('success.html', title='Регистрация',
                           description='Регистрация в электронной библиотеке', form=form)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
