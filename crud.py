import json
import random

from common import get_user_file, get_data
from constants import Constants


def print_tea_list(data):
    tea = data.get(Constants.TEA_KEY, [])
    return '\nТекущий список чая:\n   ' + '\n   '.join(tea)


def add_to_list(path, key: str, elem: str):
    with open(path, 'r+') as f:
        data = f.read()
        if data:
            data = json.loads(data)
        else:
            data = {}
        list_to_append = data.get(key, None)
        if not list_to_append:
            data[key] = []
        data.get(key).append(elem)
        f.seek(0)
        f.write(json.dumps(data))
        f.truncate()
    return data


def create_tea(message):
    tea_name = ' '.join(message.text.split()[1:])
    if tea_name == '':
        return 'Че ты мне пустой чай отправляешь?'
    data = add_to_list(get_user_file(message), Constants.TEA_KEY, tea_name)
    return 'Готово!\n' + print_tea_list(data)


def delete_tea(message):
    tea_name = ' '.join(message.text.split()[1:])
    with open(get_user_file(message), 'r+') as f:
        data = f.read()
        if data:
            data = json.loads(data)
        else:
            data = {}
        tea = data.get(Constants.TEA_KEY)
        if not tea:
            reply = 'Чай закончился, Милорд!'
        else:
            if tea_name not in tea:
                reply = 'Нет такого чая!'
            else:
                tea.remove(tea_name)
                f.seek(0)
                f.write(json.dumps(data))
                f.truncate()
                reply = 'Ок'
    reply = reply + print_tea_list(data)
    return reply


def all_tea(message):
    data = get_data(get_user_file(message))
    if len(data.get(Constants.TEA_KEY, [])) == 0:
        reply = 'Милорд! Ваша коллекция чая пуста!'
    else:
        reply = print_tea_list(data)
    return reply


def get_tea(path):
    data = get_data(path)
    tea = data.get(Constants.TEA_KEY)
    return tea or []


def get_wisdom():
    data = get_data(Constants.WISDOM_FILE).get(Constants.WISDOM_KEY) or ['Бип-боп-буп']
    return random.choice(data)


def plus_stat(path):
    with open(path, 'r+') as f:
        data = f.read()
        if data:
            data = json.loads(data)
        else:
            data = {}
        stats = data.get(Constants.STATS_KEY, None)
        if not stats:
            data[Constants.STATS_KEY] = {}
            stats = data.get(Constants.STATS_KEY, {})
        cur_date = Constants.get_date()
        cur_time = Constants.get_time()
        time_list = stats.get(cur_date, [])
        time_list.append(cur_time)
        stats[cur_date] = time_list
        f.seek(0)
        f.write(json.dumps(data))
        f.truncate()


def random_tea(message):
    data = get_tea(get_user_file(message))
    if len(data) == 0:
        reply = 'Милорд! Ваша коллекция чая пуста!'
    else:
        tea = random.choice(data)
        wisdom = get_wisdom()
        reply = wisdom + '\n\n' + tea
        plus_stat(get_user_file(message))
    return reply


def create_wisdom(message):
    wisdom = ' '.join(message.text.split()[1:])
    if wisdom == '':
        return
    data = add_to_list(Constants.WISDOM_FILE, Constants.WISDOM_KEY, wisdom)
    reply = 'Я стал мудрее.'
    return reply


def add_cup(message):
    plus_stat(get_user_file(message))
    return 'Окей, завари еще раз. В статистике отметил еще одну кружечку чая.'
