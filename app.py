from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
APP_SETTINGS = os.environ.get('APP_SETTINGS', None)
if APP_SETTINGS:
    app.config.from_object(APP_SETTINGS)
    print("APP_CONFIG={}".format(APP_SETTINGS))
else:
    print("No APP_CONFIG set in environment.")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


from models import Result


@app.route('/')
def hello():
    return "Hello World!"


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

if __name__ == '__main__':
    app.run()