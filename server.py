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
    displayed_headers = ['id', 'submission_time', 'view_number', 'title', 'message']
    questions = data_manager.filter_data(data_manager.sort_data_by_time(data_handler.get_all_questions()), displayed_headers)
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
    data_handler.save_single_answer(requested_data)

    return redirect(f'/question/{question_id}')

@app.route("/question/<question_id>/delete")
def delete_question(question_id):
    print(question_id)
    # id = question_id
    # new_list = data_manager.delete_question(id)
    # data_handler.save_all_questions(new_list)
    # print(id)
    # print(new_list)
    data_manager.delete_answers_by_question_id(question_id)
    data_manager.delete_question_by_id(question_id)
    return redirect('/')

if __name__ == "__main__":
    app.run(
        host='127.0.0.1',
        port=5050,
        debug=True)