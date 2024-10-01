import json
import random

from common import get_user_file, get_data, get_file_by_id, save_data, get_tea_list
from constants import Constants


def print_tea_list(data):
    tea = data.get(Constants.TEA_KEY, {})
    return '\nТекущий список чая:\n   ' + '\n   '.join(tea)


def create_tea(user_id, tea_name):
    if tea_name == '':
        return 'Че ты мне пустой чай отправляешь?'
    user_file = get_file_by_id(user_id)
    data = get_data(user_file)
    tea_list = get_tea_list(data)
    if tea_name in tea_list:
        return 'Такой чай уже есть!'
    if ';' in tea_name:
        return 'Название чая не должно содержать символа ";"!\nУвы =('
    tea_list[tea_name] = {}
    save_data(user_file, data)
    return 'Готово!\n' + print_tea_list(data)


def delete_tea(user_id, tea_name):
    user_file = get_file_by_id(user_id)
    data = get_data(user_file)
    tea_list = get_tea_list(data)
    if len(tea_list) == 0:
        return 'Чай закончился, Милорд!'
    if tea_name not in tea_list:
        return 'Нет такого чая!\n' + print_tea_list(data)
    tea_list.pop(tea_name)
    save_data(user_file, data)
    return f'Удалил {tea_name} из списка.\n' + print_tea_list(data)


def all_tea(message):
    data = get_data(get_user_file(message))
    if len(data.get(Constants.TEA_KEY, {})) == 0:
        reply = 'Милорд! Ваша коллекция чая пуста!'
    else:
        reply = print_tea_list(data)
    return reply


def get_wisdom():
    data = get_data(Constants.WISDOM_FILE).get(Constants.WISDOM_KEY) or ['Бип-боп-буп']
    return random.choice(data)


def plus_stat(path, tea_name=None):
    data = get_data(path)

    stats = data.get(Constants.STATS_KEY, None)
    if not stats:
        data[Constants.STATS_KEY] = {}
        stats = data.get(Constants.STATS_KEY, {})
    cur_date = Constants.get_date()
    cur_time = Constants.get_time()
    time_list = stats.get(cur_date, [])
    time_list.append(cur_time)

    if tea_name:
        tea_list = get_tea_list(data)
        teabags = tea_list.get(tea_name, {}).get('teabags', None)
        if teabags:
            teabags = int(teabags) - 1
            if teabags < 0:
                teabags = 0
            tea_list[tea_name]['teabags'] = str(teabags)

    save_data(path, data)


def random_tea(message):
    data = get_data(get_user_file(message))
    tea_list = get_tea_list(data)
    if len(tea_list) == 0:
        reply = None
    else:
        tea = random.choice(list(tea_list.keys()))
        wisdom = get_wisdom()
        reply = wisdom + '\n\n' + tea
        plus_stat(get_user_file(message), tea_name=tea)
    return reply


def create_wisdom(user_id, wisdom):
    if wisdom == '':
        return
    data = get_data(Constants.WISDOM_FILE)
    if Constants.WISDOM_KEY not in data:
        data[Constants.WISDOM_KEY] = []
    data[Constants.WISDOM_KEY].append(wisdom)
    save_data(Constants.WISDOM_FILE, data)
    reply = 'Я стал мудрее.'
    return reply


def add_cup(message):
    plus_stat(get_user_file(message))
    return 'Окей, завари еще раз. В статистике отметил еще одну кружечку чая.'
