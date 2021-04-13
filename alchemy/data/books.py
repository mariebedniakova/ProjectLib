import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Booк(SqlAlchemyBase):
    __tablename__ = 'books'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String)
    author = sqlalchemy.Column(sqlalchemy.String)
    year = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    genre = sqlalchemy.Column(sqlalchemy.String)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    # Не знаю, как хранить
    text = None
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
