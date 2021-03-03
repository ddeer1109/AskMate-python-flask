from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path

import data_manager
import time
import data_handler
import os


app = Flask(__name__)
PATH = app.root_path
# app.config["UPLOAD_FOLDER"] = data_handler.UPLOADED_IMAGES_FILE_PATH


@app.route("/")
@app.route("/list")
def get_list_of_questions():
    """Services redirection to main page with loaded list of all questions."""

    questions = data_manager.get_all_data()
    return render_template('list.html', questions=questions)


@app.route("/question/<question_id>")
def display_question(question_id):
    """Services redirection to specific question page."""

    question = data_manager.get_question_by_id(question_id)
    answers = data_manager.get_answers_for_question(question_id)

    return render_template("question.html",
                           question=question,
                           answers=answers,
                           )


@app.route("/add-question")
def display_add_question():
    """Services redirection to displaying interface of adding question"""

    return render_template("add_question.html")


@app.route("/add-question", methods=['POST'])
def add_question():
    """Services posting question."""
    question_id = data_manager.add_new_entry(
        'question',
        form_data=request.form,
        request_files=request.files)

    return redirect(url_for('display_question', question_id=question_id))


@app.route("/question/<question_id>/add-answer")
def display_add_answer(question_id):
    """Services redirection to displaying interface of adding answer."""

    return render_template('add_answer.html')


@app.route("/question/<question_id>/add-answer", methods=["POST"])
def new_answer(question_id):
    """Services posting answer."""

    data_manager.add_new_entry(
        'answer',
        form_data=request.form,
        request_files=request.files,
        question_id=question_id)

    return redirect(f'/question/{question_id}')


@app.route("/answer/<answer_id>/add-comment")
def add_answer_comment(answer_id):

    return render_template('add_comment.html', answer_id=answer_id)


@app.route("/answer/<answer_id>/add-comment", methods=['POST'])
def post_answer_comment(answer_id):

    message = request.form['message']
    redirection_id = data_manager.add_comment(message, 'answer', answer_id)
    return redirect(url_for('display_question', question_id=redirection_id))


@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    data_manager.delete_question(question_id)

    return redirect('/')


@app.route("/question/<question_id>/edit")
def edit_question(question_id):
    """Services displaying edition of question and posting edited version."""
    question = data_manager.get_single_question(question_id)
    return render_template('edit_question.html', question_id=question_id, question=question)


@app.route("/question/<question_id>/edit", methods=['POST'])
def save_edited_question(question_id):
    title = request.form['title']
    message = request.form['message']

    data_manager.save_edited_question(question_id, title, message)

    return redirect(url_for('display_question', question_id=question_id))


@app.route("/answer/<answer_id>/delete")
def delete_answer(answer_id):
    """Services deleting answer."""

    redirection_id = data_manager.delete_answer_by_id(answer_id)

    return redirect(url_for('display_question', question_id=redirection_id))


@app.route("/answer/<answer_id>/edit")
def display_answer_to_edit(answer_id):
    """Services displaying edition of answer and posting edited version."""

    answer = data_manager.get_answer(answer_id)
    return render_template('edit_answer.html', answer_id=answer_id, answer=answer)


@app.route("/answer/<answer_id>/edit", methods=['POST'])
def save_edited_answer(answer_id):
    redirection_id = data_manager.save_edited_answer(answer_id, request.form['message'])


    return redirect(url_for('display_question', question_id=redirection_id))


@app.route("/<entry_type>/<entry_id>/<vote_value>", methods=["POST"])
def vote_on_post(entry_id, vote_value, entry_type):
    """Services voting on questions and answers"""

    redirection_id = data_manager.vote_on_post(entry_id, vote_value, entry_type)

    return redirect(url_for('display_question', question_id=redirection_id))


if __name__ == "__main__":
    app.run(
        host='127.0.0.1',
        port=5050,
        debug=True)