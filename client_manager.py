from flask import session

def set_session(login):
    session['logged_user'] = login

def get_logged_user():
    return session.get('logged_user', None)