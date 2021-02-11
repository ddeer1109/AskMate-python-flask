from flask import Flask, render_template, request, redirect, url_for
# from data_handler import get_all_questions, sort_data_by_time, get_question_by_id, get_formatted_headers, get_answers_for_question, QUESTIONS_DATA_HEADER, ANSWERS_DATA_HEADER

import data_manager
import time
import data_handler


app = Flask(__name__)
PATH = app.root_path


@app.route("/")
@app.route("/list")
def get_list_of_questions():
    # git checkout
    # displayed_headers = ['id', 'submission_time', 'view_number', 'title', 'message']
    displayed_headers = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message']

    requested_query_string = request.args

    if len(requested_query_string) == 0:
        questions = data_manager.filter_data(data_manager.sort_data_by_time(data_handler.get_all_questions()), displayed_headers)
        # formatted_headers = data_manager.get_formatted_headers(displayed_headers)
        # return render_template('list.html', questions=questions, question_headers=formatted_headers)
    else:
        questions = data_manager.filter_data(data_manager.sort_data_by_sorting_key(data_handler.get_all_questions(), requested_query_string), displayed_headers)

    formatted_headers = data_manager.get_formatted_headers(displayed_headers)
    return render_template('list.html', questions=questions, question_headers=formatted_headers)



@app.route("/question/<question_id>")
def display_question(question_id):

    displayed_headers_answers = ['submission_time', 'vote_number', 'message']
    displayed_headers_question = ['id', 'submission_time', 'view_number', 'title', 'message']
    question = data_manager.filter_data([data_manager.get_question_by_id(question_id)], displayed_headers_question)[0]
    answers = data_manager.filter_data(data_manager.get_answers_for_question(question_id), displayed_headers_answers)
    return render_template("question.html",
                           question=question,
                           answers=answers,
                           question_headers=data_manager.get_formatted_headers(displayed_headers_question),
                           answer_headers=data_manager.get_formatted_headers(displayed_headers_answers)
                           )

@app.route("/question/<question_id>/add-answer")
def add_an_answer(question_id):
    return render_template('add_answer.html')

@app.route("/question/<question_id>/add-answer", methods=["POST"])
def new_answer(question_id):
    requested_data = dict(request.form)
    requested_data['submission_time'] = int(time.time())
    requested_data['vote_number'] = 0
    requested_data['image'] = 'image/image.png'
    requested_data['id'] = data_manager.get_next_answer_id()
    requested_data['question_id'] = int(question_id)
    print(requested_data)
    data_handler.save_all_answers(requested_data)

    return redirect(f'/question/{question_id}')

@app.route("/add-question")
def display_add_question():
    return render_template("add_question.html")

@app.route("/add-question", methods=['POST'])
def add_question():
    requested_data = dict(request.form)

    requested_data['id'] = data_manager.get_next_id()
    requested_data['submission_time'] = data_manager.get_current_timestamp()
    requested_data['view_number'] = 0  # TODO - further implementation needed
    requested_data['vote_number'] = 0  # TODO - further implementation needed
    requested_data['image'] = 'images/image1.png' # TODO - further implementation neede

    data_handler.save_all_questions(requested_data)

    return redirect(url_for('display_question', question_id=requested_data['id']))

if __name__ == "__main__":
    app.run(
        host='127.0.0.1',
        port=5050,
        debug=True)