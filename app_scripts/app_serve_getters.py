from app_holder import *
from data_management_scripts import client_manager as client, service_answer as ans, service_user as usr, \
    service_question as qst
from data_management_scripts.client_manager import login_required


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

    qst.update_views_count(question_id)

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


@app.route('/users')
@login_required
def users():
    # if session.get('logged_user', None):
    users = usr.get_users()
    return render_template("users.html", users=users)
    # else:
    #     return render_template("login.html", message="You have to be logged in to see users")


@app.route('/user/<user_id>')
@login_required
def user_page(user_id):
    # if session.get('logged_user', None):
    user = usr.get_user_data(user_id)
    questions = usr.get_questions_of_user(user_id)
    answers = usr.get_answers_of_user(user_id)
    comments = usr.get_comments_of_user(user_id)
    return render_template("user_page.html",
                           user=user,
                           questions=questions,
                           answers=answers,
                           comments=comments)