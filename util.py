import time
import datetime


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