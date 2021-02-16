from flask import Flask, render_template, request, redirect, url_for

import data_manager
import time
import data_handler

app = Flask(__name__)
PATH = app.root_path


@app.route("/")
@app.route("/list")
def get_list_of_questions():
    questions = data_handler.read_file(data_handler.QUESTIONS_DATA_FILE_PATH)
    requested_query_string = request.args

    questions = data_manager.sort_data(questions, requested_query_string, data_handler.QUESTIONS_DATA_HEADER)

    # format time to display nice
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
    questions = data_handler.read_file(data_handler.QUESTIONS_DATA_FILE_PATH)

    requested_data = dict(request.form)
    requested_data['id'] = str(data_manager.get_next_id(questions))
    requested_data['submission_time'] = str(data_manager.get_current_timestamp())
    requested_data['view_number'] = '0'  # TODO - further implementation needed
    requested_data['vote_number'] = '0'  # TODO - further implementation needed
    requested_data['image'] = 'images/image1.png'  # TODO - further implementation needed

    questions.append(requested_data)
    data_handler.write_file(data_handler.QUESTIONS_DATA_FILE_PATH, data_handler.QUESTIONS_DATA_HEADER, questions)

    return redirect(url_for('display_question', question_id=requested_data['id']))


@app.route("/question/<question_id>/add-answer")
def add_an_answer(question_id):
    return render_template('add_answer.html')


@app.route("/question/<question_id>/add-answer", methods=["POST"])
def new_answer(question_id):
    answers = data_handler.read_file(data_handler.ANSWER_DATA_FILE_PATH)

    requested_data = dict(request.form)
    requested_data['submission_time'] = str(data_manager.get_current_timestamp())
    requested_data['vote_number'] = '0'
    requested_data['image'] = 'image/image.png'
    requested_data['id'] = str(data_manager.get_next_answer_id(answers))
    requested_data['question_id'] = str(question_id)

    answers.append(requested_data)

    data_handler.write_file(data_handler.ANSWER_DATA_FILE_PATH, data_handler.ANSWERS_DATA_HEADER, answers)

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

# @app.route("/answer/<answer_id>/delete")
# def delete_answer(answer_id, question_id):
#     answers = data_handler.read_file(data_handler.ANSWER_DATA_FILE_PATH)
#     answers = data_manager.delete_rows(answer_id, 'id', answers)
#     data_handler.write_file(data_handler.ANSWER_DATA_FILE_PATH, data_handler.ANSWERS_DATA_HEADER, answers)
#
#     return redirect('/question/<question_id>')


# @app.route("/question/<question_id>/edit")
# def edit():
#     return render_template('edit_question.html')


@app.route("/question/<question_id>/edit", methods=["GET", "POST"])
def edit_question(question_id):
    questions = data_handler.read_file(data_handler.QUESTIONS_DATA_FILE_PATH)
    question = data_manager.get_question_by_id_without_timestamp_conversion(question_id, questions)

    if request.method == "POST":
        edited_question = dict(request.form)
        edited_question['id'] = question['id']
        edited_question['submission_time'] = question['submission_time'] # TODO further implementation needed
        edited_question['vote_number'] = question['vote_number']
        edited_question['view_number'] = question['view_number']
        edited_question['image'] = question['image']
        questions = data_manager.delete_rows(question_id, 'id', questions)
        questions.append(edited_question)
        data_handler.write_file(data_handler.QUESTIONS_DATA_FILE_PATH, data_handler.QUESTIONS_DATA_HEADER, questions)
        return redirect(f'/question/{question_id}')
    else:
        return render_template('edit_question.html', question_id=question_id, question=question)


if __name__ == "__main__":
    app.run(
        host='127.0.0.1',
        port=5050,
        debug=True)
