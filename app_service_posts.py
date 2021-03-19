from app_holder import app
from flask import url_for, redirect, request, render_template

from client_manager import get_logged_user_id, set_session, process_registration, login_required, is_authenticated

from data_management.service_comment import add_comment
from data_management.service_generic import add_new_entry
from data_management.service_tag import add_new_tag_to_db
from data_management.service_user import get_users_session_data
from data_management.service_generic import get_question_id_from_entry


@app.route("/add-question", methods=['POST'])
@login_required
def add_question():
    """Services posting question."""
    question_id = add_new_entry(
        table_name='question',
        form_data=request.form,
        request_files=request.files,
        user_id=get_logged_user_id()
        )

    return redirect(url_for('display_question', question_id=question_id))


@app.route("/question/<question_id>/add-answer", methods=["POST"])
@login_required
def new_answer(question_id):
    """Services posting answer."""

    add_new_entry(
        table_name='answer',
        form_data=request.form,
        request_files=request.files,
        question_id=question_id,
        user_id=get_logged_user_id())

    return redirect(f'/question/{question_id}')


@app.route("/<entry_type>/<entry_id>/add-comment", methods=["POST"])
@login_required
def post_comment(entry_type, entry_id):
    message = request.form['message']

    redirection_id = get_question_id_from_entry(entry_type, entry_id)

    add_comment(message, entry_type, entry_id, get_logged_user_id())

    return redirect(url_for('display_question', question_id=redirection_id))


@app.route("/question/<question_id>/new-tag", methods=['POST'])
@login_required
def add_new_tag(question_id):
    add_new_tag_to_db(request.form['tag'])
    return redirect(url_for('display_new_tag', question_id=question_id))


@app.route("/question/<question_id>/new-tag-question", methods=['POST'])
@login_required
def add_new_tag_to_question(question_id):
    add_new_tag_to_question(question_id, request.form['tag_id'])
    return redirect(url_for('display_question', question_id=question_id))


@app.route('/login', methods=['POST'])
def post_login():
    login = request.form['login']
    password = request.form['password']

    if is_authenticated(login, password):
        user = get_users_session_data(login)
        set_session(user['login'], user['id'])

        return redirect(url_for('get_five_question'))

    return render_template('login.html', message="Incorrect Login or Password")


@app.route('/registration', methods=['POST'])
def registration():
    login = request.form.get('login')
    password = request.form.get('password')

    response = process_registration(login, password)

    if response:
        return render_template('registration.html', message=response)
    else:
        return render_template('login.html', registration_message="You've been registered")

