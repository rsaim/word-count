from flask import Flask
import os

app = Flask(__name__)

APP_CONFIG = os.environ.get('APP_SETTINGS', None)
if APP_CONFIG:
    app.config.from_object(APP_CONFIG)
    print("APP_CONFIG={}".format(APP_CONFIG))
else:
    print("No APP_CONFIG set in environment.")


@app.route('/')
def hello():
    return "Hello World!"


@app.route('/<name>')
def hello_name(name):
    return "Hello {}!".format(name)

if __name__ == '__main__':
    app.run()