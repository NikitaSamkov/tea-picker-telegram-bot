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
    with open(path, 'r') as f:
        data = f.read()
        if data:
            data = json.loads(data)
        else:
            data = {}
    return data


def get_tea_by_message(message):
    data = get_data(get_user_file(message))
    return data.get(Constants.TEA_KEY)
