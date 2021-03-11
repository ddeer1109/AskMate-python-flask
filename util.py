import time
import datetime
import bcrypt

def get_current_timestamp():
    """Return current timestamp in seconds"""

    return round(int(time.time()), 0)


def get_datetime_now():
    return datetime.datetime.fromtimestamp(get_current_timestamp())


def get_image_name(image_storage_obj):
    """Checks if storage object is not empty. If it is returns default image filename else returns object filename"""

    storage_obj_empty = image_storage_obj.filename == ""
    invalid_extension = ".jpg" not in image_storage_obj.filename and ".png" not in image_storage_obj.filename

    if storage_obj_empty or invalid_extension:
        image_name = 'none.jpg'
    else:
        image_name = image_storage_obj.filename

    return image_name


def set_init_entry_values(form_data, request_files):
    requested_data = dict(form_data)
    image_filename = get_image_name(request_files['image'])

    requested_data['image'] = image_filename
    requested_data['vote_number'] = 0
    requested_data['submission_time'] = get_datetime_now()

    return requested_data


def init_complete_dict_entry(entry_type, form_data=None, request_files=None, question_id=None):
    if entry_type == 'question':
        complete_entry = set_init_entry_values(form_data, request_files)
        complete_entry['view_number'] = 0

    elif entry_type == 'answer':
        complete_entry = set_init_entry_values(form_data, request_files)
        complete_entry['question_id'] = question_id

    return complete_entry


def highlight_search_phrases_in_lists(list_of_entries, search_phrase, answers=False):

    for entry in list_of_entries:
        if answers:
            for answer in entry['answers']:
                answer['message'] = highlight_search_phrase(answer['message'], search_phrase)
        else:
            for key in ['title', 'message']:
                entry[key] = highlight_search_phrase(entry[key], search_phrase)


def highlight_search_phrase(string_message, search_phrase):
    try:
        low_message, low_phrase = str.lower(string_message), str.lower(search_phrase)

        starting_index = low_message.index(low_phrase)
        ending_index = starting_index + len(search_phrase)

        new_string = string_message[:starting_index] + \
                     '<mark>' + string_message[starting_index:ending_index] + '</mark>' \
                     + string_message[ending_index:]

        return new_string

    except ValueError:
        return string_message


def add_answer_snippets(questions_list):
    import data_manager
    for question in questions_list:
        question['answers'] = data_manager.get_answers_for_question(question['id'])



def process_phrase_searched_in_both_question_and_answer(highlighted_questions, highlighted_answers):
    ids_with_highlighted_answers = [question['id'] for question in highlighted_answers]
    indexes_to_delete = []
    for index, entry in enumerate(highlighted_questions):
        if entry['id'] in ids_with_highlighted_answers:
            replaced_item_index = ids_with_highlighted_answers.index(entry['id'])
            highlighted_answers[replaced_item_index]['title'] = entry['title']
            highlighted_answers[replaced_item_index]['message'] = entry['message']

            indexes_to_delete.append(index)

    for index in indexes_to_delete:
        del highlighted_questions[index]

def hash_given_password(password):
    password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)

    return hashed

def check_password(password, hashed):
    return bcrypt.checkpw(password, hashed)

