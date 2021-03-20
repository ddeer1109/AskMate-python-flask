from os import environ

from flask import Flask

app = Flask(__name__)
PATH = app.root_path

app.config['SECRET_KEY'] = environ.get('SECRET_KEY')

