from app_holder import *
from server import login_required
from util import get_question_id_from_entry


import service_comment as com, client_manager as client, service_answer as ans, \
    service_tag as tag, service_question as qst


@app.route("/question/<question_id>/delete")
@login_required
def delete_question(question_id):
    if client.get_post_if_permitted(question_id, 'question'):
        qst.delete_question(question_id)
        return redirect('/')
    else:
        return render_template("login.html", message="You don't have permission to perform this action")


@app.route("/question/<question_id>/tag/<tag_id>/delete")
@login_required
def delete_single_tag_from_question(question_id, tag_id):
    if client.get_post_if_permitted(question_id, 'question'):
        tag.remove_single_tag_from_question(question_id, tag_id)
        return redirect(url_for('display_question', question_id=question_id))
    else:
        return render_template("login.html", message="You don't have permission to perform this action")



@app.route("/answer/<answer_id>/delete")
@login_required
def delete_answer(answer_id):
    """Services deleting answer."""
    if client.get_post_if_permitted(answer_id, 'answer'):
        redirection_id = get_question_id_from_entry('answer', answer_id)
        ans.delete_answer_by_id(answer_id)
        return redirect(url_for('display_question', question_id=redirection_id))
    else:
        return render_template("login.html", message="You don't have permission to perform this action")


@app.route("/comment/<comment_id>/delete")
@login_required
def delete_comment(comment_id):
    if client.get_post_if_permitted(comment_id, 'comment'):
        redirection_id = get_question_id_from_entry('comment', comment_id)
        com.delete_comment_by_id(comment_id)
        return redirect(url_for('display_question', question_id=redirection_id))
    else:
        return render_template("login.html", message="You don't have permission to perform this action")

