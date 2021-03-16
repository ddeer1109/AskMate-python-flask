from flask import session
import data_manager

def set_session(login, id):
    session['logged_user'] = login
    session['user_id'] = id

def drop_session():
    session.pop('logged_user', None)
    session.pop('user_id', None)

def get_logged_user():
    return session.get('logged_user', None)

def get_logged_user_id():
    return session.get('user_id', None)

def get_post_if_permitted(post_id, post_type):
    user_post = None
    logged_user_id = get_logged_user_id()

    if logged_user_id:
        user_post = data_manager.get_user_post(logged_user_id, post_id, post_type)

    return user_post