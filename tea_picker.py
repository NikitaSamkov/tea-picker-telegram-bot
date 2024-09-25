import json
import os.path
import random
from datetime import datetime
from configparser import ConfigParser
import matplotlib.pyplot as plt
import matplotlib.dates as matplotlib_dates

import telebot


class Constants:
    TEA_KEY = 'tea'
    WISDOM_KEY = 'wisdom'
    USER_DIR = 'user-data'
    WISDOM_FILE = 'wisdom.json'
    STATS_KEY = 'stats'
    CUP_ML = 300
    NEEDED_ML = 3700
    STATS_REACTIONS = {
        0: 'Я не понял, ты почему еще не начал?',
        2: 'НЕДОСТАТОЧНО',
        3: 'Неплохо!',
        5: 'С кайфом провёл денёк',
        7: 'Преисполнился в чае',
        10: 'Упился',
        12: 'ЧАЙ ТЕЧЁТ В НАШИХ ВЕНАХ, СОГРЕВАЯ СЕРДЦА',
        15: 'Ты вообще работаешь?',
        20: 'Охренеть.'
    }
    SETTINGS_DIR = 'settings'
    SETTINGS_FILE = 'settings'
    GRAPH_MAX_DAYS = 30

    @staticmethod
    def get_date():
        return datetime.today().strftime('%d-%m-%Y')

    @staticmethod
    def get_date_from_str(str_date: str):
        return datetime.strptime(str_date, '%d-%m-%Y')

    @staticmethod
    def get_time():
        return datetime.now().strftime('%H:%M:%S')

    @staticmethod
    def get_time_from_str(str_time: str):
        return datetime.strptime(str_time, '%H:%M:%S')


def init_settings():
    settings_tmpl = os.path.join(Constants.SETTINGS_DIR, f'{Constants.SETTINGS_FILE}.template')
    if not os.path.exists(settings_tmpl):
        raise NotImplementedError('Не объявлен шаблон настроек!')
    config_tmpl = ConfigParser()
    config_tmpl.read(settings_tmpl)
    bot_token = input('Введите токен бота: ')
    config_tmpl.set('bot_settings', 'BOT_TOKEN', bot_token)
    with open(os.path.join(Constants.SETTINGS_DIR, Constants.SETTINGS_FILE), 'w') as settings_f:
        config_tmpl.write(settings_f)
    print('Токен сохранён!')


plt.switch_backend('agg')
settings_path = os.path.join(Constants.SETTINGS_DIR, Constants.SETTINGS_FILE)
if not os.path.exists(settings_path):
    init_settings()
config = ConfigParser()
config.read(settings_path)

bot = telebot.TeleBot(config.get('bot_settings', 'BOT_TOKEN'))


@bot.message_handler(commands=['start'])
def start(message):
    reply = 'Привет!' \
            '\nЯ - твой помощник в выборе чая (☕☕☕) в эти тяжёлые времена!' \
            '\nАвтор: Самков Н. А. (https://online.sbis.ru/person/d4ea3ef3-98f2-4057-9c88-eee341795833)' \
            '\nКоманды:' \
            '\n/add_tea - Добавить чай в пул' \
            '\n/delete - Удалить чай из пула (кончился)' \
            '\n/tea_list - Список чая' \
            '\n/pick - Выбрать чай из пула' \
            '\n/statistics - Получить статистику по выпитому чаю за сегодня'
    bot.send_message(message.from_user.id, reply)


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


def get_tea(path):
    data = get_data(path)
    tea = data.get(Constants.TEA_KEY)
    return tea or []


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


def print_tea_list(data):
    tea = data.get(Constants.TEA_KEY, [])
    return '\nТекущий список чая:\n   ' + '\n   '.join(tea)


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


@bot.message_handler(commands=['add_tea'])
def add_tea(message):
    tea_name = ' '.join(message.text.split()[1:])
    if tea_name == '':
        bot.send_message(message.from_user.id, 'Че ты мне пустой чай отправляешь?')
        return
    data = add_to_list(get_user_file(message), Constants.TEA_KEY, tea_name)
    reply = 'Готово!\n' + print_tea_list(data)
    bot.send_message(message.from_user.id, reply)


@bot.message_handler(commands=['delete'])
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
            bot.send_message(message.from_user.id, 'Чай закончился, Милорд!')
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
    bot.send_message(message.from_user.id, reply)


@bot.message_handler(commands=['tea_list'])
def tea_list(message):
    data = get_data(get_user_file(message))
    if len(data.get(Constants.TEA_KEY, [])) == 0:
        reply = 'Милорд! Ваша коллекция чая пуста!'
    else:
        reply = print_tea_list(data)
    bot.send_message(message.from_user.id, reply)


@bot.message_handler(commands=['pick'])
def tea_pick(message):
    data = get_tea(get_user_file(message))
    if len(data) == 0:
        reply = 'Милорд! Ваша коллекция чая пуста!'
    else:
        tea = random.choice(data)
        wisdom = get_wisdom()
        reply = wisdom + '\n\n' + tea
        plus_stat(get_user_file(message))
    bot.send_message(message.from_user.id, reply)


@bot.message_handler(commands=['add_wisdom'])
def add_wisdom(message):
    wisdom = ' '.join(message.text.split()[1:])
    if wisdom == '':
        return
    data = add_to_list(Constants.WISDOM_FILE, Constants.WISDOM_KEY, wisdom)
    reply = 'Я стал мудрее.'
    bot.send_message(message.from_user.id, reply)


@bot.message_handler(commands=['statistics'])
def get_stats(message):
    reply = '========================\nСТАТИСТИКА\n========================'
    data = get_data(get_user_file(message))
    stats = data.get(Constants.STATS_KEY, {})
    cur_date = Constants.get_date()
    cups = len(stats.get(cur_date, []))
    reply = reply + '\n' + f'За сегодня ты выпил {cups} кружек чая.'
    ml = cups * Constants.CUP_ML
    reply = reply + '\n' + f'А это, на секунду, {ml}мл чая!'
    percent = (ml * 100) // Constants.NEEDED_ML
    reply = reply + '\n' + f'Кроме того, это {percent}% от суточной нормы воды!'
    prev_reaction = ''
    for needed_cups, reaction in Constants.STATS_REACTIONS.items():
        if needed_cups > cups:
            break
        prev_reaction = reaction
    reply = reply + '\n\n' + prev_reaction
    bot.send_message(message.from_user.id, reply)


@bot.message_handler(commands=['plus_cup'])
def plus_cup(message):
    plus_stat(get_user_file(message))
    reply = 'Окей, завари еще раз. В статистике отметил еще одну кружечку чая.'
    bot.send_message(message.from_user.id, reply)


def calculate_tea_speed(cups_timestaps):
    cups_time = []
    cups_speed = []
    for i in range(len(cups_timestaps) - 1):
        cur_time = Constants.get_time_from_str(cups_timestaps[i])
        cups_time.append(cur_time)
        time_diff = Constants.get_time_from_str(cups_timestaps[i + 1]) - cur_time
        hours = time_diff.total_seconds() / 60 / 24
        cups_speed.append(round(1 / hours, 2))
    return cups_time, cups_speed


def set_today_speed_graph(stats, axis):
    cur_date = Constants.get_date()
    cups = stats.get(cur_date, [])
    axis.set_title('Скорость питья чая за сегодня')
    if len(cups) < 2:
        return
    cups_time, cups_speed = calculate_tea_speed(cups)
    axis.plot(cups_time, cups_speed, linewidth=3)
    axis.set_xlabel('Время')
    axis.set_ylabel('Скорость (кружек в час)')
    axis.xaxis.set_major_formatter(matplotlib_dates.DateFormatter('%H:%M'))


def set_today_count_graph(stats, axis):
    cur_date = Constants.get_date()
    cups = stats.get(cur_date, [])
    axis.set_title('Количество выпитого чая за сегодня')
    cups_time = list(map(Constants.get_time_from_str, cups))
    cups_count = [i + 1 for i in range(len(cups))]
    axis.plot(cups_time, cups_count, linewidth=3)
    axis.set_xlabel('Время')
    axis.set_ylabel('Количество кружек')
    axis.xaxis.set_major_formatter(matplotlib_dates.DateFormatter('%H:%M'))


def set_daily_count_graph(stats, axis):
    axis.set_title('Количество кружек чая по дням')
    if len(stats) < 2:
        return
    dates = [Constants.get_date_from_str(item) for item in list(stats.keys())[-Constants.GRAPH_MAX_DAYS:]]
    counts = [len(item) for item in list(stats.values())[-Constants.GRAPH_MAX_DAYS:]]
    axis.plot(dates, counts, linewidth=3)
    axis.set_xlabel('Дата')
    axis.set_ylabel('Кружки')
    axis.tick_params(axis='x', rotation=45)
    axis.xaxis.set_major_formatter(matplotlib_dates.DateFormatter('%d-%m-%Y'))


def set_daily_speed_graph(stats, axis):
    axis.set_title('Средняя скорость питья чая по дням')
    if len(stats) < 2:
        return
    dates = []
    mid_speed = []
    for date in list(stats.keys())[-Constants.GRAPH_MAX_DAYS:]:
        dates.append(Constants.get_date_from_str(date))
        timestamps = stats.get(date, [])
        if len(timestamps) < 2:
            mid_speed.append(0)
        else:
            _, cups_speed = calculate_tea_speed(timestamps)
            mid_speed.append(round(sum(cups_speed) / len(cups_speed), 2))
    axis.plot(dates, mid_speed, linewidth=3)
    axis.set_xlabel('Дата')
    axis.set_ylabel('Средняя скорость (кружек в час)')
    axis.tick_params(axis='x', rotation=45)
    axis.xaxis.set_major_formatter(matplotlib_dates.DateFormatter('%d-%m-%Y'))


@bot.message_handler(commands=['tea_graph'])
def tea_graph(message):
    plt.clf()
    data = get_data(get_user_file(message))
    stats = data.get(Constants.STATS_KEY, {})
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))
    plt.title('Статистика чая')

    set_today_speed_graph(stats, axs[0, 0])
    set_today_count_graph(stats, axs[0, 1])
    set_daily_speed_graph(stats, axs[1, 0])
    set_daily_count_graph(stats, axs[1, 1])

    plt.tight_layout()
    plt.savefig(os.path.join(Constants.USER_DIR, f'{message.from_user.id}.png'))

    with open(os.path.join(Constants.USER_DIR, f'{message.from_user.id}.png'), 'rb') as photo:
        bot.send_photo(message.from_user.id, photo)


bot.polling(none_stop=True, interval=0)
