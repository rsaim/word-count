#!/usr/bin/env python
import os
import requests
import operator
import re
import nltk
from flask import Flask, render_template, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from stop_words import stops
from collections import Counter
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize

from rq import Queue
from rq.job import Job
from worker import conn

app = Flask(__name__)

# $ heroku config:set APP_SETTINGS=config.StagingConfig --remote stage
# $ heroku config:set APP_SETTINGS=config.ProductionConfig --remote pro
APP_SETTINGS = os.environ.get('APP_SETTINGS', None)
if APP_SETTINGS:
    app.config.from_object(APP_SETTINGS)
    print("APP_CONFIG={}".format(APP_SETTINGS))
else:
    print("No APP_CONFIG set in environment.")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

q = Queue(connection=conn)


def count_and_save_words(url):
    errors = []
    try:
        if not url.startswith("http"):
            url = 'http://' + url
        print("Counting words from {!r}".format(url))
        r = requests.get(url)
    except Exception as err:
        errors.append(f"Unable to get URL. Please make sure it's "
                      f"valid and try again: {err}")
        return {"errors": errors}

    # text processing
    raw = BeautifulSoup(r.text, 'html.parser').get_text()
    nltk.data.path.append('./nltk_data/')  # set the path
    tokens = nltk.word_tokenize(raw)
    text = nltk.Text(tokens)

    # remove punctuation, count raw words
    nonPunct = re.compile('.*[A-Za-z].*')
    raw_words = [w for w in text if nonPunct.match(w)]
    raw_word_count = Counter(raw_words)

    # stop words
    no_stop_words = [w for w in raw_words if w.lower() not in stops]
    no_stop_words_count = Counter(no_stop_words)

    try:
        # save the results
        from models import Result
        result = Result(
            url=url,
            result_all=raw_word_count,
            result_no_stop_words=no_stop_words_count
        )
        db.session.add(result)
        db.session.commit()
        print(f"{url} processed; id={result.id}")
        return result.id
    except Exception as err:
        print(f"Error while parsing {url}: {err}")
        errors.append("Unable to add item to database: {!r}".format(err))
        return {"errors": errors}


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/start', methods=['POST'])
def get_counts():
    print("/start endpoint")
    errors = []
    # get url that the person has entered
    # This works when the params are encoded in url (Content-Type: application/x-www-form-urlencoded)
    # url = request.form['url']
    # Following works wtih Content-Type:'multipart / form - data'
    url = request.get_json()["url"]
    job = q.enqueue_call(func=count_and_save_words,
                         args=(url,),
                         result_ttl=5000)
    print(job.id)
    return job.get_id()


@app.route("/results/<job_key>", methods=["GET"])
def get_results(job_key):

    job = Job.fetch(job_key, connection=conn)

    if job.is_finished:
        from models import Result
        result = Result.query.filter_by(id=job.result).first()
        results = sorted(result.result_no_stop_words.items(),
                         key=operator.itemgetter(1),
                         reverse=True)[:30]
        return jsonify(results)
    else:
        return "Nay!", 202

@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)


if __name__ == '__main__':
    app.run()
