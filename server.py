from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path

import data_manager
import time
import data_handler
import os


app = Flask(__name__)
PATH = app.root_path
app.config["UPLOAD_FOLDER"] = data_handler.UPLOADED_IMAGES_FILE_PATH


@app.route("/")
@app.route("/list")
def get_list_of_questions():
    questions = data_handler.read_file(data_handler.QUESTIONS_DATA_FILE_PATH)
    requested_query_string = request.args

    questions = data_manager.sort_data(questions, requested_query_string, data_handler.QUESTIONS_DATA_HEADER)

    formatted_headers = data_manager.get_formatted_headers(data_handler.QUESTIONS_DATA_HEADER)

    return render_template('list.html', questions=questions, question_headers=formatted_headers)


@app.route("/question/<question_id>")
def display_question(question_id):
    questions = data_handler.read_file(data_handler.QUESTIONS_DATA_FILE_PATH)
    answers = data_handler.read_file(data_handler.ANSWER_DATA_FILE_PATH)

    single_question = data_manager.get_question_by_id(question_id, questions)
    single_question_answers = data_manager.get_answers_for_question(question_id, answers)

    question = data_manager.filter_data([single_question], data_handler.QUESTIONS_DATA_HEADER)[0]
    answers = data_manager.filter_data(single_question_answers, data_handler.ANSWERS_DATA_HEADER)

    return render_template("question.html",
                           question=question,
                           answers=answers,
                           question_headers=data_manager.get_formatted_headers(data_handler.QUESTIONS_DATA_HEADER),
                           answer_headers=data_manager.get_formatted_headers(data_handler.ANSWERS_DATA_HEADER)
                           )


@app.route("/add-question")
def display_add_question():
    return render_template("add_question.html")


@app.route("/add-question", methods=['POST'])
def add_question():

    question_id = data_manager.add_new_question(request.form, request.files)

    return redirect(url_for('display_question', question_id=question_id))


@app.route("/question/<question_id>/add-answer")
def add_an_answer(question_id):
    return render_template('add_answer.html')


@app.route("/question/<question_id>/add-answer", methods=["POST"])
def new_answer(question_id):

    data_manager.add_new_answer(request.form, request.files, question_id)

    return redirect(f'/question/{question_id}')


@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    answers = data_handler.read_file(data_handler.ANSWER_DATA_FILE_PATH)
    questions = data_handler.read_file(data_handler.QUESTIONS_DATA_FILE_PATH)

    answers = data_manager.delete_rows(question_id, 'question_id', answers)
    questions = data_manager.delete_rows(question_id, 'id', questions)

    data_handler.write_file(data_handler.ANSWER_DATA_FILE_PATH, data_handler.ANSWERS_DATA_HEADER, answers)
    data_handler.write_file(data_handler.QUESTIONS_DATA_FILE_PATH, data_handler.QUESTIONS_DATA_HEADER, questions)

    return redirect('/')


@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    questions = data_handler.read_file(data_handler.QUESTIONS_DATA_FILE_PATH)
    question = data_manager.get_question_by_id_without_timestamp_conversion(question_id, questions)

    if request.method == "POST":
        data_manager.edit_entry(dict(request.form), question, questions)
        return redirect(f'/question/{question_id}')
    else:
        return render_template('edit_question.html', question_id=question_id, question=question)


@app.route("/question/answer/<answer_id>/edit", methods=["GET", "POST"])
def edit_answer(answer_id):
    answers = data_handler.read_file(data_handler.ANSWER_DATA_FILE_PATH)
    answer = data_manager.get_question_by_id_without_timestamp_conversion(answer_id, answers)

    if request.method == "POST":
        data_manager.edit_entry(request.form, answer, answers)
        return redirect(f'/question/{answer["question_id"]}')
    else:
        return render_template('edit_answer.html', answer_id=answer_id, answer=answer)


@app.route("/<entry_type>/<entry_id>/<vote_value>", methods=["POST"])
@app.route("/<entry_type>/<entry_id>/<vote_value>", methods=["POST"])
def vote_on_post(entry_id, vote_value, entry_type):

    redirection_id = data_manager.vote_on_post(entry_id, vote_value, entry_type)

    return redirect(url_for('display_question', question_id=redirection_id))


if __name__ == "__main__":
    app.run(
        host='127.0.0.1',
        port=5050,
        debug=True)
