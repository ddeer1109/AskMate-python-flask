from flask import request, redirect, url_for

from app_holder import app
#### IMPORTANT TO ASK ABOUT IMPORTING GOOD PRACTICES

from data_management import \
        service_answer as ans, \
        service_question as qst, \
        service_comment as com, \
        service_user as usr

from data_management.service_generic import get_question_id_from_entry
from client_manager import process_voting, get_logged_user_id, login_required


@app.route("/question/<question_id>/edit", methods=['POST'])
@login_required
def save_edited_question(question_id):
    title = request.form['title']
    message = request.form['message']

    qst.save_edited_question(question_id, title, message)

    return redirect(url_for('display_question', question_id=question_id))


@app.route("/answer/<answer_id>/edit", methods=['POST'])
@login_required
def save_edited_answer(answer_id):
    ans.save_edited_answer(answer_id, request.form['message'])
    redirection_id = get_question_id_from_entry('answer', answer_id)

    return redirect(url_for('display_question', question_id=redirection_id))


@app.route("/comment/<comment_id>/edit", methods=["POST"])
@login_required
def edit_comment(comment_id):
    new_message = request.form['message']
    com.update_comment(comment_id, new_message)

    redirection_id = get_question_id_from_entry('comment', comment_id)

    return redirect(url_for('display_question', question_id=redirection_id))


@app.route("/<entry_type>/<entry_id>/<vote_value>", methods=["POST"])
@login_required
def vote_on_post(entry_id, vote_value, entry_type):
    """Services voting on questions and answers"""
    process_voting(entry_id, vote_value, entry_type)
    redirection_id = get_question_id_from_entry(entry_type, entry_id)

    if entry_type == 'answer':
        usr.add_user_answer_activity(get_logged_user_id(), entry_id)
    else:
        usr.add_user_question_activity(get_logged_user_id(), entry_id)

    return redirect(url_for('display_question', question_id=redirection_id))
