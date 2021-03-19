from os import environ

from flask import Flask, render_template, request, redirect, url_for, session


app = Flask(__name__)
PATH = app.root_path

app.config['SECRET_KEY'] = environ.get('SECRET_KEY')




@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404