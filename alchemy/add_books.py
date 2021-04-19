# noinspection PyUnresolvedReferences
from data.books import Book
# noinspection PyUnresolvedReferences
from data.db_session import global_init, create_session
from flask_wtf import FlaskForm
from wtforms import TextField, BooleanField, SubmitField
from wtforms import IntegerField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from flask import Flask, render_template, redirect

from flask_login import LoginManager, login_user, login_required, current_user

class AccessError(Exception):
    pass

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
global_init("db/library.db")





@app.route('/addbook',  methods=['GET', 'POST'])
@login_required
def add_job():
    try:
        if not current_user.is_authenticated:
            return redirect('/library/login')
        if not current_user.admin:
            return AccessError
        form = BooksForm()
        if form.validate_on_submit():
            db_sess = create_session()
            book = Book()
            book.title = form.title.data
            book.author = form.author.data
            book.year = form.year.data
            book.genre = form.genre.data
            book.description = form.description.data
            db_sess.add(book)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/library')
    except AccessError:
        return # ругается на отсутствие прав доступа
    return render_template('books.html', title='Добавление книги',
                           form=form)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')

# to do: возможность зарегестрироваться при входе и войти при регистрации
# редактирование удаление и получение книги. примитивные html


