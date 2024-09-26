import json
import os

from constants import Constants


def get_user_file(message):
    user_id = str(message.from_user.id)
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
