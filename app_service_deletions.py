from flask import redirect, url_for, render_template

from app_holder import app
#### IMPORTANT TO ASK ABOUT IMPORTING GOOD PRACTICES
from data_management.service_question import delete_question as question_process_delete_in_server
from data_management.service_answer import delete_answer_by_id
from data_management.service_comment import delete_comment_by_id
from data_management.service_tag import remove_single_tag_from_question
from data_management.service_generic import get_question_id_from_entry

from client_manager import get_post_if_permitted, drop_session, login_required


@app.route("/question/<question_id>/delete")
@login_required
def delete_question(question_id):
    if get_post_if_permitted(question_id, 'question'):
        question_process_delete_in_server(question_id)
        return redirect('/')
    else:
        return render_template("login.html", message="You don't have permission to perform this action")


@app.route("/answer/<answer_id>/delete")
@login_required
def delete_answer(answer_id):
    """Services deleting answer."""
    if get_post_if_permitted(answer_id, 'answer'):
        redirection_id = get_question_id_from_entry('answer', answer_id)
        delete_answer_by_id(answer_id)
        return redirect(url_for('display_question', question_id=redirection_id))
    else:
        return render_template("login.html", message="You don't have permission to perform this action")


@app.route("/comment/<comment_id>/delete")
@login_required
def delete_comment(comment_id):
    if get_post_if_permitted(comment_id, 'comment'):
        redirection_id = get_question_id_from_entry('comment', comment_id)
        delete_comment_by_id(comment_id)
        return redirect(url_for('display_question', question_id=redirection_id))
    else:
        return render_template("login.html", message="You don't have permission to perform this action")


@app.route("/question/<question_id>/tag/<tag_id>/delete")
@login_required
def delete_single_tag_from_question(question_id, tag_id):
    if get_post_if_permitted(question_id, 'question'):
        remove_single_tag_from_question(question_id, tag_id)
        return redirect(url_for('display_question', question_id=question_id))
    else:
        return render_template('login.html', not_allowed_message="Only post's author may manage this post.")




@app.route('/logout')
def logout():
    drop_session()
    return redirect(url_for('display_5_questions_list'))

