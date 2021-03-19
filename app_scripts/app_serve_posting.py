
from app_holder import *

from data_management_scripts import service_comment as com, client_manager as client, service_tag as tag

from data_management_scripts.util import get_question_id_from_entry
from data_management_scripts.data_manager import add_new_entry
from data_management_scripts.client_manager import login_required


@app.route("/add-question")
@login_required
def display_add_question():
    """Services redirection to displaying interface of adding question"""
    # if session.get('logged_user', None):
    return render_template("add_question.html")
    # else:
    #     return render_template("login.html", message="You have to be logged in to add questions or answers")


@app.route("/add-question", methods=['POST'])
@login_required
def add_question():
    """Services posting question."""
    question_id = add_new_entry(
        table_name='question',
        form_data=request.form,
        request_files=request.files,
        user_id=client.get_logged_user_id()
        )

    # add_user_question_activity(session['user_id'], question_id)

    return redirect(url_for('display_question', question_id=question_id))


@app.route("/question/<question_id>/add-answer")
@login_required
def display_add_answer(question_id):
    """Services redirection to displaying interface of adding answer."""
    # if session.get('logged_user', None):
    return render_template("add_answer.html")
    # else:
    #     return render_template("login.html", message="You have to be logged in to add questions or answers")


@app.route("/question/<question_id>/add-answer", methods=["POST"])
@login_required
def new_answer(question_id):
    """Services posting answer."""

    answer_id = add_new_entry(
        table_name='answer',
        form_data=request.form,
        request_files=request.files,
        question_id=question_id,
        user_id=client.get_logged_user_id())

    # add_user_answer_activity(session['user_id'], answer_id)

    return redirect(f'/question/{question_id}')


@app.route("/answer/<answer_id>/add-comment")
@login_required
def add_answer_comment(answer_id):
    return render_template('add_answer_comment.html', answer_id=answer_id)


@app.route("/answer/<answer_id>/add-comment", methods=['POST'])
@login_required
def post_answer_comment(answer_id):
    message = request.form['message']
    com.add_comment(message, 'answer', answer_id, client.get_logged_user_id())
    redirection_id = get_question_id_from_entry('answer', answer_id)

    return redirect(url_for('display_question', question_id=redirection_id))


@app.route("/question/<question_id>/add-comment")
@login_required
def display_add_comment(question_id):
    return render_template('add_comment.html')


@app.route("/question/<question_id>/add-comment", methods=["POST"])
@login_required
def post_question_comment(question_id):
    com.add_comment(request.form['message'], 'question', question_id, client.get_logged_user_id())
    return redirect(f'/question/{question_id}')


@app.route("/question/<question_id>/new-tag")
@login_required
def display_new_tag(question_id):
    all_tags = tag.get_all_tags()
    return render_template('new_tag.html',
                           question_id=question_id,
                           all_tags=all_tags
                           )

@app.route("/question/<question_id>/new-tag", methods=['POST'])
@login_required
def add_new_tag(question_id):
    tag.add_new_tag_to_db(request.form['tag'])
    return redirect(url_for('display_new_tag', question_id=question_id))


@app.route("/question/<question_id>/new-tag-question", methods=['POST'])
@login_required
def add_new_tag_to_question(question_id):
    print(request.form['tag_id'])
    message = tag.add_new_tag_to_question(question_id, request.form['tag_id'])
    return redirect(url_for('display_question', question_id=question_id))


#