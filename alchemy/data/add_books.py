# noinspection PyUnresolvedReferences
from books import Book
# noinspection PyUnresolvedReferences
from data import db_session
from flask_wtf import FlaskForm
from wtforms import PasswordField, BooleanField, SubmitField
from wtforms import IntegerField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from flask import Flask, render_template, redirect

from flask_login import LoginManager, login_user, login_required, current_user


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
db_session.global_init("db/library.db")

@
class JobsForm(FlaskForm):
    job = StringField('Работа', validators=[DataRequired()])
    work_size = IntegerField("Время работы")
    team_leader_id = IntegerField('ID ответственного', validators=[DataRequired()])
    collaborators = StringField('ID участников', validators=[DataRequired()])
    is_finished = BooleanField("Завeршена?")
    submit = SubmitField('Применить')

@app.route('/addjob',  methods=['GET', 'POST'])
@login_required
def add_job():
    form = JobsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = Jobs()
        print(form.job.data, form.work_size.data, form.team_leader_id.data, form.collaborators.data, form.is_finished.data)
        job.job = form.job.data
        job.work_size = form.work_size.data
        job.team_leader = form.team_leader_id.data
        job.collaborators = form.collaborators.data
        job.is_finished = form.is_finished.data
        db_sess.add(job)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('jobs.html', title='Добавление работы',
                           form=form)
if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')


class BookListResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('title', required=True)
    parser.add_argument('author', required=True)
    parser.add_argument('year', required=True, type=int)
    parser.add_argument('genre', required=True)
    parser.add_argument('description', required=True)

