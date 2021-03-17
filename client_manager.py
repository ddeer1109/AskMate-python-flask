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


def process_voting(entry_id, vote_value, entry_type):
    if get_logged_user() is not None:
        user_id = get_logged_user_id()
        user_vote = data_manager.get_user_vote(user_id, (f'{entry_type}_id', entry_id))

        if user_vote is None:
            redirection_id = data_manager.vote_on_post(entry_id, vote_value, entry_type)

            vote_value = 1 if vote_value == "vote_up" else -1
            if entry_type == 'question':
                data_manager.add_vote(user_id, vote_value, question_id=entry_id)
            else:
                data_manager.add_vote(user_id, vote_value, answer_id=entry_id)
        else:
            redirection_id = data_manager.clear_vote(user_vote)

        return redirection_id


def get_voted_posts_to_render(question_id, answers_ids):
    if get_logged_user():
        user_id = session.get('user_id', None)

        states = {1: {'vote_up': 'disabled', 'vote_down': 'active'},
                  -1: {'vote_up': 'active', 'vote_down': 'disabled'},
                  0: {'vote_up': '', 'vote_down': ''}}

        question_vote = data_manager.get_user_vote(user_id, ('question_id', question_id))

        if question_vote:
            question_vote = states[question_vote['vote_value']]
        else:
            question_vote = states[0]

        answers = {}
        for ans_id in answers_ids:
            answer_vote = data_manager.get_user_vote(user_id, ('answer_id', ans_id))
            if answer_vote:
                answers[ans_id] = states[answer_vote['vote_value']]
            else:
                answers[ans_id] = states[0]

        return question_vote, answers
