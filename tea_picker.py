import datetime
import json
import os.path
import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException
from configparser import ConfigParser

from admin import clear_empty_records, clear_old_records, clear_png
from constants import Constants
from common import get_tea_names, get_tea_list, get_data, get_file_by_id, get_user_file, update_info
from crud import delete_tea, all_tea, random_tea, add_cup
from statistics import get_statistics, generate_graph, get_week_stats
from settings import init_settings, log
from separated_arguments import SAC
from tea_metadata import get_metadata, get_tea_info, get_tea_meta, edit_tea_info

settings_path = os.path.join(Constants.SETTINGS_DIR, Constants.SETTINGS_FILE)
if not os.path.exists(settings_path):
    init_settings()
config = ConfigParser()
config.read(settings_path)

bot = telebot.TeleBot(config.get('bot_settings', 'BOT_TOKEN'))

print('[БОТ ЗАПУЩЕН]')


def send_message(user_message, reply, markup=None):
    try:
        update_info(message=user_message)
        log(user_message)
        bot.send_message(user_message.chat.id, reply, reply_markup=markup)
    except ApiTelegramException as err:
        user = user_message.from_user
        print(f'Ошибка для пользователя {user.username} ({user.last_name} {user.first_name}) [{user.id}]: {err}')


@bot.message_handler(commands=['start'])
def start(message):
    reply = 'Привет!' \
            '\nЯ - твой помощник в выборе чая (☕☕☕) в эти тяжёлые времена!' \
            '\nАвтор: Самков Н. А. (https://vk.com/nikitasamkov)' \
            '\nКоманды:' \
            '\n/add_tea - Добавить чай в пул' \
            '\n/delete - Удалить чай из пула (кончился)' \
            '\n/tea_list - Список чая' \
            '\n/pick - Выбрать чай из пула' \
            '\n/statistics - Получить статистику по выпитому чаю за сегодня' \
            '\n/tea_graph - Получить статистику в графиках'
    send_message(message, reply)


@bot.message_handler(commands=['add_tea'])
def add_tea(message):
    reply = SAC.prepare('add_tea', message) or 'Напиши же мне название чая:'
    send_message(message, reply)


@bot.message_handler(commands=['delete'])
def remove_tea(message):
    user_id = message.from_user.id
    args = ' '.join(message.text.split(' ')[1:])
    if args:
        reply = delete_tea(user_id, args)
        send_message(message, reply)
        return
    tea = get_tea_names(message)
    if len(tea) == 0:
        send_message(message, 'Ваша коллекция чая пуста!')
        return
    reply = 'Какой чай удалить из пула?\n' + '\n'.join(tea)
    buttons = []
    for tea_name in tea:
        buttons.append([types.InlineKeyboardButton(tea_name, callback_data=f'delete;{user_id};{tea_name}')])
    markup = types.InlineKeyboardMarkup(buttons)
    send_message(message, reply, markup)


@bot.callback_query_handler(func=lambda call: call.data.split(';')[0] == 'delete')
def delete_tea_handler(call):
    data_split = call.data.split(';')
    if len(data_split) > 2:
        message = call.message
        user_id = data_split[1]
        tea_name = data_split[2]
        reply = delete_tea(user_id, tea_name)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=reply)


@bot.message_handler(commands=['tea_list'])
def tea_list(message):
    reply = all_tea(message)
    send_message(message, reply)


@bot.message_handler(commands=['pick'])
def tea_pick(message):
    reply = random_tea(message)
    if reply is None:
        send_message(message, 'Милорд! Ваша коллекция чая пуста!')
        return
    send_message(message, reply)


@bot.message_handler(commands=['add_wisdom'])
def add_wisdom(message):
    reply = SAC.prepare('add_wisdom', message) or 'Напиши мудрость, чтобы я её запомнил:'
    send_message(message, reply)


@bot.message_handler(commands=['statistics'])
def get_stats(message):
    reply = get_statistics(message)
    send_message(message, reply)


@bot.message_handler(commands=['plus_cup'])
def plus_cup(message):
    reply = add_cup(message)
    send_message(message, reply)


@bot.message_handler(commands=['tea_graph'])
def tea_graph(message):
    user_id = message.from_user.id
    args = ' '.join(message.text.split(' ')[1:])
    if args:
        generate_graph(user_id, args, config)
        with open(os.path.join(Constants.USER_DIR, f'{message.from_user.id}.png'), 'rb') as photo:
            bot.send_photo(message.from_user.id, photo)
        return
    cur_date = datetime.datetime.now()
    buttons = [[], [], []]
    for i in range(-10, 1, 1):
        to_add = cur_date + datetime.timedelta(days=i)
        str_date = to_add.strftime('%d.%m')
        if i == 0:
            str_date = '[СЕГОДНЯ] ' + str_date
        buttons[0 if i < -5 else 1 if i < 0 else 2].append(
            types.InlineKeyboardButton(str_date, callback_data=f"tea_graph;{user_id};{to_add.strftime('%d.%m.%Y')}"))
    markup = types.InlineKeyboardMarkup(buttons)
    send_message(message, 'Выберите дату:', markup)


@bot.callback_query_handler(func=lambda call: call.data.split(';')[0] == 'tea_graph')
def tea_graph_handler(call):
    call_data = call.data.split(';')
    if len(call_data) > 2:
        message = call.message
        bot.edit_message_text('Ваш график:', message.chat.id, message.message_id)
        user_id = call_data[1]
        date = call_data[2]
        generate_graph(user_id, date, config)
        with open(os.path.join(Constants.USER_DIR, f'{user_id}.png'), 'rb') as photo:
            bot.send_photo(call.message.chat.id, photo)


@bot.message_handler(commands=['week_stats'])
def week_stats(message):
    reply = get_week_stats(message)
    send_message(message, reply)


@bot.message_handler(commands=['metadata'])
def all_metadata(message):
    reply = 'Текущие доступные метаданные:\n'
    metadata = get_metadata()
    messages = []
    for meta_id, meta_value in metadata.items():
        name = meta_value.get('name', 'UNKNOWN')
        values = meta_value.get('values', [])
        to_add = f'{name}\n   id: {meta_id}'
        if values:
            to_add += '\n   Доступные значения: ' + ', '.join(map(lambda item: f'"{item}"', values))
        messages.append(to_add)
    reply += '\n\n'.join(messages)
    send_message(message, reply)


@bot.message_handler(commands=['tea_info'])
def tea_info(message):
    user_id = message.from_user.id
    args = ' '.join(message.text.split(' ')[1:])
    if args:
        reply = get_tea_info(user_id, args)
        send_message(message, reply)
        return
    tea = get_tea_names(message)
    if len(tea) == 0:
        send_message(message, 'Ваша коллекция чая пуста!')
        return
    reply = 'Выберите чай:\n' + '\n'.join(tea)
    buttons = []
    for tea_name in tea:
        buttons.append([types.InlineKeyboardButton(tea_name, callback_data=f'info;{user_id};{tea_name}')])
    markup = types.InlineKeyboardMarkup(buttons)
    send_message(message, reply, markup)


@bot.callback_query_handler(func=lambda call: call.data.split(';')[0] == 'info')
def tea_info_handler(call):
    data_split = call.data.split(';')
    if len(data_split) > 2:
        message = call.message
        user_id = data_split[1]
        tea_name = data_split[2]
        reply = get_tea_info(user_id, tea_name)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=reply)


@bot.message_handler(commands=['edit_tea'])
def edit_tea(message):
    user_id = message.from_user.id
    args = ' '.join(message.text.split(' ')[1:])
    if args:
        reply = get_tea_info(user_id, args)
        send_message(message, reply)
        return
    tea = get_tea_names(message)
    if len(tea) == 0:
        send_message(message, 'Ваша коллекция чая пуста!')
        return
    reply = 'Выберите чай:\n' + '\n'.join(tea)
    buttons = []
    for tea_name in tea:
        buttons.append([types.InlineKeyboardButton(tea_name, callback_data=f'edit;{user_id};{tea_name}')])
    markup = types.InlineKeyboardMarkup(buttons)
    send_message(message, reply, markup)


@bot.callback_query_handler(func=lambda call: call.data.split(';')[0] == 'edit')
def edit_tea_handler(call):
    data_split = call.data.split(';')
    if len(data_split) > 2:
        message = call.message
        user_id = data_split[1]
        tea_name = data_split[2]

        tea_meta = get_tea_meta(get_tea_list(get_data(get_file_by_id(user_id))).get(tea_name))
        reply = f'[{tea_name}]\n\n' + \
                '\n'.join([(Constants.MARK_SYMBOL if item.get('value') is not None else Constants.CROSS_SYMBOL) +
                           ' ' + item.get('name') +
                           ((': ' + str(item.get('value'))) if item.get('value') is not None else '')
                           for item in tea_meta])

        buttons = []
        for i, (meta_id, meta_info) in enumerate(get_metadata().items()):
            if meta_info.get('hidden', None) is True:
                continue
            button_row = i // 2
            if len(buttons) <= button_row:
                buttons.append([])
            callback = f'edit_{meta_id};{user_id};{tea_name}'
            buttons[button_row].append(types.InlineKeyboardButton(meta_info.get('name'), callback_data=callback))

        markup = types.InlineKeyboardMarkup(buttons)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=reply, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.split(';')[0].startswith('edit_'))
def edit_meta_handler(call):
    data_split = call.data.split(';')
    if len(data_split) > 2:
        message = call.message
        user_id = int(data_split[1])
        tea_name = data_split[2]
        meta_id = '_'.join(data_split[0].split('_')[1:])

        metadata = get_metadata().get(meta_id, None)
        if metadata is None:
            print(f'Метадата с ид {meta_id} не найдена!')
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                  text='Сожалею, данный аттрибут пока изменять нельзя.')
            return

        if len(data_split) == 4:
            value_idx = data_split[3]
            values = metadata.get('values', None)
            value = value_idx if not values or not value_idx.isnumeric() or len(values) <= int(value_idx) \
                else values[int(value_idx)]
            reply = edit_tea_info(user_id, value, tea_name, meta_id)
            callback = f'edit;{user_id};{tea_name}'
            markup = types.InlineKeyboardMarkup([[types.InlineKeyboardButton('Назад', callback_data=callback)]])
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=reply)
            bot.edit_message_reply_markup(chat_id=message.chat.id, message_id=message.message_id, reply_markup=markup)
            return

        values = metadata.get('values', None)
        if values:
            buttons = []
            for i, item in enumerate(values):
                callback = f'edit_{meta_id};{user_id};{tea_name};{i}'
                if len(callback.encode('utf-8')) > 64:
                    send_message(message, 'К сожалению, этот аттрибут пока менять нельзя')
                    return
                buttons.append([types.InlineKeyboardButton(item, callback_data=callback)])
            markup = types.InlineKeyboardMarkup(buttons)
            reply = f'[{tea_name}]\n\n{metadata.get("name")}:'
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=reply,
                                  reply_markup=markup)
            return

        SAC.prepare('edit_tea_info', user_id=user_id, extra_args={'tea_name': tea_name, 'meta_id': meta_id})
        reply = f'Напишите значение для аттрибута "{metadata.get("name")}":'
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=reply)


@bot.message_handler(commands=['clear_empty'])
def clear_empty(message):
    user_id = message.from_user.id
    if str(user_id) != config.get('admin', 'ADMIN_ID', fallback=-1):
        return bot.send_message(message.chat.id, 'Вы не являетесь администратором!')
    reply = clear_empty_records()
    send_message(message, reply)


@bot.message_handler(commands=['clear_old'])
def clear_old(message):
    user_id = message.from_user.id
    if str(user_id) != config.get('admin', 'ADMIN_ID', fallback=-1):
        return bot.send_message(message.chat.id, 'Вы не являетесь администратором!')
    reply = clear_old_records()
    send_message(message, reply)


@bot.message_handler(commands=['clear_pics'])
def clear_pics(message):
    user_id = message.from_user.id
    if str(user_id) != config.get('admin', 'ADMIN_ID', fallback=-1):
        return bot.send_message(message.chat.id, 'Вы не являетесь администратором!')
    reply = clear_png()
    send_message(message, reply)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    reply = SAC.launch(message.from_user.id, message.text)

    if reply:
        markup = types.ReplyKeyboardRemove()
        send_message(message, reply, markup)


bot.infinity_polling(timeout=10, long_polling_timeout=5)
