from flask import Flask, render_template, request, redirect, url_for
# from data_handler import get_all_questions, sort_data_by_time, get_question_by_id, get_formatted_headers, get_answers_for_question, QUESTIONS_DATA_HEADER, ANSWERS_DATA_HEADER
from data_manager import *
from data_handler import save_all_questions
app = Flask(__name__)

@app.route("/")
@app.route("/list")
def get_list_of_questions():
    displayed_headers = ['id', 'submission_time', 'view_number', 'title', 'message']
    questions = filter_data(sort_data_by_time(get_all_questions()), displayed_headers)
    formatted_headers = get_formatted_headers(displayed_headers)
    return render_template('list.html', questions=questions, question_headers=formatted_headers)


@app.route("/question/<question_id>")
def display_question(question_id):

    displayed_headers_answers = ['submission_time', 'vote_number', 'message']
    displayed_headers_question = ['id', 'submission_time', 'view_number', 'title', 'message']
    question = filter_data([get_question_by_id(question_id)], displayed_headers_question)[0]
    answers = filter_data(get_answers_for_question(question_id), displayed_headers_answers)
    return render_template("question.html",
                           question=question,
                           answers=answers,
                           question_headers=get_formatted_headers(displayed_headers_question),
                           answer_headers=get_formatted_headers(displayed_headers_answers)
                           )

@app.route("/add-question")
def display_add_question():
    return render_template("add_question.html")

@app.route("/add-question", methods=['POST'])
def add_question():
    requested_data = dict(request.form)

    # vote_number, title, message, image
    requested_data['id'] = get_next_id()
    requested_data['submission_time'] = get_current_timestamp()
    requested_data['view_number'] = 11  # TODO - further implementation needed
    requested_data['vote_number'] = 7  # TODO - further implementation needed
    requested_data['image'] = 'images/image1.png' # TODO - further implementation neede

    save_all_questions(requested_data)

    return redirect(url_for('display_question', question_id=requested_data['id']))

if __name__ == "__main__":
    app.run(
        host='127.0.0.1',
        port=5050,
        debug=True)