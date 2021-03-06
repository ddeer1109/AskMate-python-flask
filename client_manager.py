from data_management.service_question import update_views_count
from data_management.service_user import create_new_user, get_user_vote, get_user_post, is_existing_user, is_password_ok
from flask import session, render_template
from functools import wraps

from data_management import service_generic, util
import random

sessions_visited_questions = dict()


def set_session(login, id):
    session['session_id'] = str(random.randint(0, 200))+random.choice('abcdef')
    session['logged_user'] = login
    session['user_id'] = id
    sessions_visited_questions[session['session_id']] = []


def drop_session():
    session.pop('logged_user', None)
    session.pop('user_id', None)
    sessions_visited_questions.pop(session.get('session_id'), None)


def get_logged_user():
    return session.get('logged_user', None)


def get_logged_user_id():
    return session.get('user_id', None)


def get_post_if_permitted(post_id, post_type):
    user_post = None
    logged_user_id = get_logged_user_id()

    if logged_user_id:
        user_post = get_user_post(logged_user_id, post_id, post_type)

    return user_post


def process_registration(login, password):
    if is_existing_user(login):
        return "Login is not available"

    password = util.hash_given_password(password)
    create_new_user(login, password)

    return ""


def process_views_update(question_id):
    try:
        if get_logged_user() is not None:
            if question_id not in sessions_visited_questions.get(session.get('session_id', None), None):
                update_views_count(question_id)
                mark_question_as_visited_in_this_session(question_id)
    except KeyError:
        drop_session()
        return
    except TypeError:
        drop_session()
        return


def mark_question_as_visited_in_this_session(question_id):
    sessions_visited_questions[session['session_id']].append(question_id)


def process_voting(entry_id, vote_value, entry_type):
    if get_logged_user() is not None:
        user_id = get_logged_user_id()
        user_vote = get_user_vote(user_id, (f'{entry_type}_id', entry_id))

        if user_vote is None:
            service_generic.vote_on_post(entry_id, vote_value, entry_type)

            vote_value = 1 if vote_value == "vote_up" else -1
            if entry_type == 'question':
                service_generic.add_vote(user_id, vote_value, question_id=entry_id)
            else:
                service_generic.add_vote(user_id, vote_value, answer_id=entry_id)
        else:
            service_generic.clear_vote(user_vote)


def get_voted_posts_to_render(question_id, answers_ids):
    if get_logged_user():
        user_id = session.get('user_id', None)

        states = {1: {'vote_up': 'disabled', 'vote_down': 'active'},
                  -1: {'vote_up': 'active', 'vote_down': 'disabled'},
                  0: {'vote_up': '', 'vote_down': ''}}

        question_vote = get_user_vote(user_id, ('question_id', question_id))

        if question_vote:
            question_vote = states.get(question_vote.get('vote_value'))
        else:
            question_vote = states[0]

        answers = {}
        for ans_id in answers_ids:
            answer_vote = get_user_vote(user_id, ('answer_id', ans_id))
            if answer_vote:
                answers[ans_id] = states[answer_vote.get('vote_value')]
            else:
                answers[ans_id] = states[0]

        return question_vote, answers


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if get_logged_user_id() is None:
            return render_template("login.html", message="You have to be logged in to perform this action.")
        return f(*args, **kwargs)
    return decorated_function


def is_authenticated(login, password):
    return is_existing_user(login) and is_password_ok(login, password)

