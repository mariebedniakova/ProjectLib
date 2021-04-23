from flask import Flask, render_template, redirect
# noinspection PyUnresolvedReferences
from data.users import User
# noinspection PyUnresolvedReferences
from data.books import Book
# noinspection PyUnresolvedReferences
from data import db_session
from data.forms import OkForm, BooksForm, LoginForm, RegistrationForm
from flask_login import LoginManager, login_user, login_required, current_user, logout_user

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
users_book = {}
all_books = None


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@login_required
@app.route('/library/<user_email>/addbook/<int:book_id>')
def add_book_to_user(user_email, book_id):
    global users_book
    db_sess = db_session.create_session()
    book = db_sess.query(Book).get(book_id)
    if user_email not in users_book:
        users_book[user_email] = []
    if book not in users_book[user_email]:
        users_book[user_email].append(book)
    return redirect("/library")


@app.route('/library/registration', methods=['GET', 'POST'])
def registration():
    form = RegistrationForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()

        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            email=form.email.data,
            hashed_password=form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/library/successful_registration")
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


@app.route('/library/<user_email>', methods=['GET', 'POST'])
def account(user_email):
    user = current_user
    if user.email not in users_book:
        users_book[user_email] = []
    return render_template('account.html', title=user.name,
                           description='Электронная библиотека', books=users_book[user.email])


@app.route('/library/menu', methods=['GET', 'POST'])
def menu():
    return render_template('menu.html', title='Меню',
                           description='Электронная библиотека', current_user=current_user)


@app.route('/library/logout')
@login_required
def logout():
    logout_user()
    return redirect('/library')


@login_required
@app.route('/library', methods=['GET', 'POST'])
def home_page():
    db_sess = db_session.create_session()
    books = db_sess.query(Book).all()
    return render_template('home_page.html', title='YLibrary',
                           description='YLibrary', books=books, current_user=current_user,
                           users_books=users_book)


@app.route('/library/access_error', methods=['GET', 'POST'])
def access_error(name):
    form = OkForm()
    if form.validate_on_submit():
        return redirect('/library/login')
    return render_template('result.html', title=name,
                           description=name,
                           result='не доступна.', form=form)


@app.route('/library/<int:book_id>')
def book_page(book_id):
    if not current_user.is_authenticated:
        access_error('Информация о книге')
    db_sess = db_session.create_session()
    book = db_sess.query(Book).get(book_id)
    return render_template('book_page.html', book=book, books=users_book)


@app.route('/library/<int:book_id>/text')
def book_text(book_id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).get(book_id)
    return book.text


@app.route('/library/successful_registration', methods=['GET', 'POST'])
def successful_registration():
    form = OkForm()
    if form.validate_on_submit():
        return redirect('/library/login')
    return render_template('result.html', title='Регистрация',
                           description='Регистрация в электронной библиотеке',
                           result='прошла успешно.', form=form)


@app.route('/library/addbook', methods=['GET', 'POST'])
@login_required
def add_book():
    if not current_user.is_authenticated:
        return redirect('/library/login')
        # не работает
    if not current_user.admin:
        access_error('Добавление книги')
    form = BooksForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        book = Book()
        book.title = form.title.data
        book.author = form.author.data
        book.year = form.year.data
        book.genre = form.genre.data
        book.description = form.description.data
        book.text = form.text.data
        db_sess.add(book)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/library')

    return render_template('add_book_page.html', title='Добавление книги', ddescription='Добавление книги',
                           form=form)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
