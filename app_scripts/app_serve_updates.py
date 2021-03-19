from app_holder import *
from data_management_scripts.util import get_question_id_from_entry
from data_management_scripts.client_manager import login_required

from data_management_scripts import service_comment as com, client_manager as client, service_answer as ans, \
    service_user as usr, service_question as qst


@app.route("/question/<question_id>/edit")
@login_required
def edit_question(question_id):
    """Services displaying edition of question and posting edited version."""
    if client.get_post_if_permitted(question_id, 'question'):
        question = qst.get_single_question(question_id)
        return render_template('edit_question.html', question_id=question_id, question=question)
    else:
        return render_template("login.html", message="You don't have permission to perform this action")


@app.route("/question/<question_id>/edit", methods=['POST'])
@login_required
def save_edited_question(question_id):
    title = request.form['title']
    message = request.form['message']

    qst.save_edited_question(question_id, title, message)

    return redirect(url_for('display_question', question_id=question_id))


@app.route("/answer/<answer_id>/edit")
@login_required
def display_answer_to_edit(answer_id):
    """Services displaying edition of answer and posting edited version."""
    if client.get_post_if_permitted(answer_id, 'answer'):
        answer = ans.get_answer(answer_id)
        return render_template('edit_answer.html', answer_id=answer_id, answer=answer)
    else:
        return render_template("login.html", message="You don't have permission to perform this action")



@app.route("/answer/<answer_id>/edit", methods=['POST'])
@login_required
def save_edited_answer(answer_id):
    ans.save_edited_answer(answer_id, request.form['message'])
    redirection_id = get_question_id_from_entry('answer', answer_id)

    return redirect(url_for('display_question', question_id=redirection_id))


@app.route("/<entry_type>/<entry_id>/<vote_value>", methods=["POST"])
@login_required
def vote_on_post(entry_id, vote_value, entry_type):
    """Services voting on questions and answers"""
    # if client.get_post_if_permitted(entry_id, entry_type):
    client.process_voting(entry_id, vote_value, entry_type)
    redirection_id = get_question_id_from_entry(entry_type, entry_id)

    if entry_type == 'answer':
        usr.add_user_answer_activity(client.get_logged_user_id(), entry_id)
    else:
        usr.add_user_question_activity(client.get_logged_user_id(), entry_id)

    return redirect(url_for('display_question', question_id=redirection_id))
    # else:
    #     return render_template("login.html", message="You don't have permission to perform this action")


@app.route("/comment/<comment_id>/edit")
@login_required
def display_comment_edit(comment_id):
    if client.get_post_if_permitted(comment_id, 'comment'):
        comment = com.get_comment_by_id(comment_id)
        return render_template('edit_comment.html',
                               message=comment['message'],
                               comment_id=comment_id)
    else:
        return render_template("login.html", message="You don't have permission to perform this action")


@app.route("/comment/<comment_id>/edit", methods=["POST"])
@login_required
def edit_comment(comment_id):
    new_message = request.form['message']
    com.update_comment(comment_id, new_message)

    redirection_id = get_question_id_from_entry('comment', comment_id)

    return redirect(url_for('display_question', question_id=redirection_id))

