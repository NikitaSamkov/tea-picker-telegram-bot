import json
import os

from constants import Constants


def get_user_file(message):
    user_id = str(message.from_user.id)
    return get_file_by_id(user_id)


def get_file_by_id(user_id):
    path = os.path.join(Constants.USER_DIR, f'{user_id}.json')
    if not os.path.exists(path):
        f = open(path, 'w')
        f.close()
    return path


def get_data(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
        if data:
            data = json.loads(data)
        else:
            data = {}
    return data


def save_data(path, data):
    with open(path, 'r+', encoding='utf-8') as f:
        f.seek(0)
        f.write(json.dumps(data, indent=2))
        f.truncate()
    return data


def convert_data(data):
    new_data = {key: {} for key in data}
    return new_data


def convert_if_need(data):
    if Constants.TEA_KEY not in data:
        data[Constants.TEA_KEY] = {}
    if not isinstance(data.get(Constants.TEA_KEY, {}), dict):
        data[Constants.TEA_KEY] = convert_data(data[Constants.TEA_KEY])


def get_tea_list(data):
    convert_if_need(data)
    return data[Constants.TEA_KEY]


def get_tea_names(message):
    return list(get_tea_list(get_data(get_user_file(message))).keys())
