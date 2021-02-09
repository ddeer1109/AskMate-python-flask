from flask import Flask, render_template, request, redirect, url_for
from data_handler import get_all_questions, sort_data_by_time, get_question_by_id, get_formatted_headers, get_answers_for_question

app = Flask(__name__)


# @app.route("/")
# def hello():
#     return "Hello World!!!"

@app.route("/")
@app.route("/list")
def get_list_of_questions():
    questions = get_all_questions()
    question_headers = get_formatted_headers(datatype="question")
    questions = sort_data_by_time(questions)
    return render_template('list.html', questions=questions, question_headers=question_headers)


@app.route("/question/<question_id>")
def display_question(question_id):
    question_headers = get_formatted_headers(datatype="question")
    answer_headers = get_formatted_headers(datatype="answer")
    question = get_question_by_id(question_id)
    answers = get_answers_for_question(question_id)
    return render_template("question.html", question=question, answers=answers, question_headers=question_headers, answer_headers=answer_headers)


if __name__ == "__main__":
    app.run(
        host='127.0.0.1',
        port=5050,
        debug=True)