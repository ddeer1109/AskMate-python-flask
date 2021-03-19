from flask import render_template, request
from app_holder import app
from data_management import \
        service_answer as ans, \
        service_tag as tag, \
        service_question as qst, \
        service_comment as com, \
        service_user as usr

import client_manager as client


#
#          ------>> DISPLAY OF CONTENT <<------
#

@app.route("/")
def get_five_question():
    """Services redirection to main page with loaded list of the 5 latest questions."""
    questions = qst.get_five_questions()
    return render_template('list.html', questions=questions, sorted=False)


@app.route("/list")
def get_list_of_questions():
    """Services redirection to main page with loaded list of all questions."""
    if len(request.args) == 0:
        questions = qst.get_all_data()
    else:
        questions = qst.get_all_data_by_query(request.args.get('order_by'),
                                              request.args.get('order_direction'))

    return render_template('list.html', questions=questions, sorted=True)


@app.route("/search")
def get_entries_by_search_phrase():
    search_phrase = request.args.get('q')

    questions, questions_with_answers = qst.get_entries_by_search_phrase(search_phrase)
    highlighted_questions_id = [question['id'] for question in questions_with_answers]
    return render_template("list.html",
                           searched=True,
                           questions=questions + questions_with_answers,
                           questions_id_with_highlighted_answers=highlighted_questions_id)


@app.route("/question/<question_id>")
def display_question(question_id):
    """Services redirection to specific question page."""

    client.process_views_update(question_id)

    question = qst.get_question_by_id(question_id)
    answers = ans.get_answers_for_question(question_id)
    tags = qst.get_tags_for_question(question_id)
    comments = qst.get_comments_for_question(question_id)
    question_to_render = []
    answers_to_render = {}

    if client.get_logged_user_id():
        answer_ids = [answer['id'] for answer in answers]
        question_to_render, answers_to_render = client.get_voted_posts_to_render(question['id'], answer_ids)

    return render_template("question.html",
                           question=question,
                           answers=answers,
                           tags=tags,
                           comments=comments,
                           question_to_render=question_to_render,
                           answers_to_render=answers_to_render
                           )

#
#          ------>> DISPLAY OF INSERTS CONTENT  <<------
#

@app.route("/add-question")
@client.login_required
def display_add_question():
    """Services redirection to displaying interface of adding question"""
    # if session.get('logged_user', None):
    return render_template("add_question.html")
    # else:
    #     return render_template("login.html", message="You have to be logged in to add questions or answers")


@app.route("/question/<question_id>/add-answer")
@client.login_required
def display_add_answer(question_id):
    """Services redirection to displaying interface of adding answer."""
    # if session.get('logged_user', None):
    return render_template("add_answer.html")
    # else:
    #     return render_template("login.html", message="You have to be logged in to add questions or answers")


@app.route("/<entry_type>/<entry_id>/add-comment")
@client.login_required
def display_add_comment(entry_type, entry_id):
    return render_template('add_comment.html',
                           entry_type=entry_type,
                           entry_id=entry_id)


@app.route("/question/<question_id>/new-tag")
@client.login_required
def display_new_tag(question_id):
    all_tags = tag.get_all_tags()
    return render_template('new_tag.html',
                           question_id=question_id,
                           all_tags=all_tags
                           )


#
#          ------>> DISPLAY OF EDITION CONTENT  <<------
#

@app.route("/question/<question_id>/edit")
@client.login_required
def edit_question(question_id):
    """Services displaying edition of question and posting edited version."""
    if client.get_post_if_permitted(question_id, 'question'):
        question = qst.get_single_question(question_id)
        return render_template('edit_question.html', question_id=question_id, question=question)
    else:
        return render_template("login.html", message="You don't have permission to perform this action")


@app.route("/answer/<answer_id>/edit")
@client.login_required
def display_answer_to_edit(answer_id):
    """Services displaying edition of answer and posting edited version."""
    if client.get_post_if_permitted(answer_id, 'answer'):
        answer = ans.get_answer(answer_id)
        return render_template('edit_answer.html', answer_id=answer_id, answer=answer)
    else:
        return render_template("login.html", message="You don't have permission to perform this action")


@app.route("/comment/<comment_id>/edit")
@client.login_required
def display_comment_edit(comment_id):
    if client.get_post_if_permitted(comment_id, 'comment'):
        comment = com.get_comment_by_id(comment_id)
        return render_template('edit_comment.html',
                               message=comment['message'],
                               comment_id=comment_id)
    else:
        return render_template("login.html", message="You don't have permission to perform this action")

#
#          ------>> DISPLAY OF USER RELATED ACTIONS <<------
#


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/registration')
def display_registration():
    return render_template('registration.html')


@app.route('/users')
@client.login_required
def users():
    users = usr.get_users()
    return render_template("users.html", users=users)


@app.route('/user/<user_id>')
@client.login_required
def user_page(user_id):
    user = usr.get_user_data(user_id)
    questions = usr.get_questions_of_user(user_id)
    answers = usr.get_answers_of_user(user_id)
    comments = usr.get_comments_of_user(user_id)
    return render_template("user_page.html",
                           user=user,
                           questions=questions,
                           answers=answers,
                           comments=comments)