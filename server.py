from flask import Flask, render_template, request, redirect, url_for
# from data_handler import get_all_questions, sort_data_by_time, get_question_by_id, get_formatted_headers, get_answers_for_question, QUESTIONS_DATA_HEADER, ANSWERS_DATA_HEADER
import data_manager
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

@app.route("/question/<question_id>/add-answer", methods = ['POST', 'GET'])
def add_an_answer(question_id):
    if request.method == 'POST':
        answers = data_handler.get_data('answer.csv', PATH)
        question_data = data_handler.get_data('question.csv', PATH)
        question = [q for q in question_data if question_data[0] == question_id]
        answer = request.form['answer']
        answer_to_save = [question_id, answer]
        data_handler.save_data(PATH, 'answer.csv', answer_to_save)
        return redirect(url_for('question', question_id=question_id))
    else:
        answers = data_handler.get_data('answer.csv', PATH)
        question_data = data_handler.get_data('question.csv', PATH)
        question = [q for q in question_data if question_data[0] == question_id]
        answer = [a for a in answers if answers[0] == question_id]
        return render_template('add_answer.html', question=question, answer=answer, question_id=question_id, )

if __name__ == "__main__":
    app.run(
        host='127.0.0.1',
        port=5050,
        debug=True)