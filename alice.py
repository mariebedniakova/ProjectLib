from flask import Flask, request
from random import choice
from alchemy.data.db_session import global_init, create_session
from alchemy.data.books import Book
import pymorphy2
import logging
import json
import csv

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
morph = pymorphy2.MorphAnalyzer()

# словарь с кнопками
sessionStorage = {}
bookStatistic = {}
questions = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response)
    logging.info(f'Response:  {response!r}')
    return json.dumps(response)


def chose_a_book(user_id):
    if not bookStatistic[user_id]:
        return

    return max(bookStatistic.items(), key=lambda x: x[1])[0]


# получает из csv вопросы и возможные  ответы, формирует словарь
def get_questions(user_id):
    with open('alice_data/questions.csv', encoding="utf8") as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in reader:
            questions[user_id][row[0]] = row[1:]


# случайным вобразом выбирает вопрос, передает необходимые кнопки, возвращает вопрос
def make_a_guestion(user_id):
    if not questions[user_id]:
        get_questions(user_id)
    ques = choice(questions.keys())

    # пользоветель всегда может остановить сессию
    sessionStorage[user_id] = {
        'suggests': questions[user_id][ques].append('стоп!')
    }
    # удалим вопрос для соответствующего пользователя, чтобы не повторяться
    del questions[user_id][ques]
    return ques


# на основе ответов пользователя формируем статистику (по количеству вхождений слов в описание и название)
def make_statistic(ans, user_id, genre=False, author=False):
    global_init("db/library.db")
    db_sess = create_session()
    if genre:
        ans = ans
        for book in db_sess.query(Book).filter(Book.genre.lower().like(f"%{ans.lower()}%")):
            if book.title not in bookStatistic[user_id]:
                bookStatistic[user_id][book.title] = 0
            bookStatistic[user_id][book.title] += 10
        return
    if author:
        ans = ans
        for book in db_sess.query(Book).filter(Book.author.lower().like(ans.lower())):
            if book.title not in bookStatistic[user_id]:
                bookStatistic[user_id][book.title] = 0
            bookStatistic[user_id][book.title] += 10
        return
    ans = set(map(lambda x: morph.parse(x)[0].normal_form, filter(lambda x: len(x) > 3, ans.split())))
    for book in db_sess.query(Book).filter(
            set(map(lambda x: morph.parse(x)[0].normal_form, Book.title.split())) & ans):
        if book.title not in bookStatistic[user_id]:
            bookStatistic[user_id][book.title] = 0
        bookStatistic[user_id][book.title] += 10
    for book in db_sess.query(Book).filter(
            set(map(lambda x: morph.parse(x)[0].normal_form, Book.description.split())) & ans):
        if book.title not in bookStatistic[user_id]:
            bookStatistic[user_id][book.title] = 0
        bookStatistic[user_id][book.title] += len([(set(map(lambda x: morph.parse(x)[0].normal_form,
                                                            Book.description.split())) & ans)])


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        # Запишем подсказки, которые мы ему покажем в первый раз

        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Давай!",
            ]
        }
        # Заполняем текст ответа
        res['response']['text'] = 'Привет! Давай подберем тебе книгу!'
        # Получим подсказки
        res['response']['buttons'] = get_suggests(user_id)
        return

    # если пользователя хавершвет диалог,
    if req['request']['original_utterance'].lower() == 'стоп!' or (not questions):
        res['response']['buttons'], title = get_suggests(user_id, last=True)
        res['response']['text'] = f"Как насчет {title}?"
        return
    if req['request']['original_utterance'].lower() == 'Не хочу.':
        res['response']['text'] = f"И не надо."
        res['response']['end_session'] = True
        return
    answer = req['request']['original_utterance']
    if 'жанр' in res['response']['text']:
        make_statistic(answer, user_id, genre=True)
    if 'автор' in res['response']['text']:
        make_statistic(answer, user_id, author=True)
    res['response']['text'] = make_a_guestion(user_id)
    res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id, last=False):
    session = sessionStorage[user_id]

    # Выбираем подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests']
    ]

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if last:
        title = chose_a_book(user_id)
        suggests = [{
            "title": 'Посмотрю',
            "url": "<ссылка на книгу>",
            "hide": True
        }]
        return suggests, title

    return suggests


if __name__ == '__main__':
    app.run()
