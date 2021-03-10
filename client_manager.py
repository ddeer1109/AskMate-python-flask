from flask import session

def set_session(login, id):
    session['logged_user'] = login
    session['user_id'] = id

def drop_session():
    session.pop('logged_user', None)
    session.pop('user_id', None)

def get_logged_user():
    return session.get('logged_user', None)