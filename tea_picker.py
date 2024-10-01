import datetime
import os.path
import telebot
from telebot import types
from configparser import ConfigParser

from constants import Constants
from common import get_tea_names, get_tea_list, get_data, get_file_by_id
from crud import delete_tea, all_tea, random_tea, add_cup
from statistics import get_statistics, generate_graph, get_week_stats
from settings import init_settings
from separated_arguments import SAC
from tea_metadata import get_metadata, get_tea_info, get_tea_meta, edit_tea_info

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
            '\nАвтор: Самков Н. А. (https://vk.com/nikitasamkov)' \
            '\nКоманды:' \
            '\n/add_tea - Добавить чай в пул' \
            '\n/delete - Удалить чай из пула (кончился)' \
            '\n/tea_list - Список чая' \
            '\n/pick - Выбрать чай из пула' \
            '\n/statistics - Получить статистику по выпитому чаю за сегодня' \
            '\n/tea_graph - Получить статистику в графиках'
    bot.send_message(message.from_user.id, reply)


@bot.message_handler(commands=['add_tea'])
def add_tea(message):
    reply = SAC.prepare('add_tea', message) or 'Напиши же мне название чая:'
    bot.send_message(message.from_user.id, reply)


@bot.message_handler(commands=['delete'])
def remove_tea(message):
    user_id = message.from_user.id
    args = ' '.join(message.text.split(' ')[1:])
    if args:
        reply = delete_tea(user_id, args)
        bot.send_message(message.from_user.id, reply)
        return
    tea = get_tea_names(message)
    if len(tea) == 0:
        bot.send_message(message.from_user.id, 'Ваша коллекция чая пуста!')
        return
    reply = 'Какой чай удалить из пула?\n' + '\n'.join(tea)
    buttons = []
    for tea_name in tea:
        buttons.append([types.InlineKeyboardButton(tea_name, callback_data=f'delete;{user_id};{tea_name}')])
    markup = types.InlineKeyboardMarkup(buttons)
    bot.send_message(message.from_user.id, reply, reply_markup=markup)


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
    bot.send_message(message.from_user.id, reply)


@bot.message_handler(commands=['pick'])
def tea_pick(message):
    reply = random_tea(message)
    bot.send_message(message.from_user.id, reply)


@bot.message_handler(commands=['add_wisdom'])
def add_wisdom(message):
    reply = SAC.prepare('add_wisdom', message) or 'Напиши мудрость, чтобы я её запомнил:'
    bot.send_message(message.from_user.id, reply)


@bot.message_handler(commands=['statistics'])
def get_stats(message):
    reply = get_statistics(message)
    bot.send_message(message.from_user.id, reply)


@bot.message_handler(commands=['plus_cup'])
def plus_cup(message):
    reply = add_cup(message)
    bot.send_message(message.from_user.id, reply)


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
    bot.send_message(user_id, 'Выберите дату:', reply_markup=markup)


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
            bot.send_photo(user_id, photo)


@bot.message_handler(commands=['week_stats'])
def week_stats(message):
    reply = get_week_stats(message)
    bot.send_message(message.from_user.id, reply)


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
    bot.send_message(message.from_user.id, reply)


@bot.message_handler(commands=['tea_info'])
def tea_info(message):
    user_id = message.from_user.id
    args = ' '.join(message.text.split(' ')[1:])
    if args:
        reply = get_tea_info(user_id, args)
        bot.send_message(message.from_user.id, reply)
        return
    tea = get_tea_names(message)
    if len(tea) == 0:
        bot.send_message(message.from_user.id, 'Ваша коллекция чая пуста!')
        return
    reply = 'Выберите чай:\n' + '\n'.join(tea)
    buttons = []
    for tea_name in tea:
        buttons.append([types.InlineKeyboardButton(tea_name, callback_data=f'info;{user_id};{tea_name}')])
    markup = types.InlineKeyboardMarkup(buttons)
    bot.send_message(message.from_user.id, reply, reply_markup=markup)


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
        bot.send_message(message.from_user.id, reply)
        return
    tea = get_tea_names(message)
    if len(tea) == 0:
        bot.send_message(message.from_user.id, 'Ваша коллекция чая пуста!')
        return
    reply = 'Выберите чай:\n' + '\n'.join(tea)
    buttons = []
    for tea_name in tea:
        buttons.append([types.InlineKeyboardButton(tea_name, callback_data=f'edit;{user_id};{tea_name}')])
    markup = types.InlineKeyboardMarkup(buttons)
    bot.send_message(message.from_user.id, reply, reply_markup=markup)


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
                           ((' - ' + item.get('value')) if item.get('value') is not None else '') for item in tea_meta])

        buttons = []
        for meta_id, meta_info in get_metadata().items():
            buttons.append([types.InlineKeyboardButton(meta_info.get('name'),
                                                       callback_data=f'edit_{meta_id};{user_id};{tea_name}')])

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

        if len(data_split) == 4:
            value = data_split[3]
            reply = edit_tea_info(user_id, value, tea_name, meta_id)
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=reply)
            return

        metadata = get_metadata().get(meta_id, None)
        if metadata is None:
            print(f'Метадата с ид {meta_id} не найдена!')
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                                  text='Сожалею, данный аттрибут пока изменять нельзя.')
            return

        values = metadata.get('values', None)
        if values:
            markup = types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(item, callback_data=f'edit_{meta_id};{user_id};{tea_name};{item}')]
                for item in values])
            reply = f'[{tea_name}]\n\n{metadata.get("name")}:'
            bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=reply,
                                  reply_markup=markup)
            return

        SAC.prepare('edit_tea_info', user_id=user_id, extra_args={'tea_name': tea_name, 'meta_id': meta_id})
        reply = f'Напишите значение для аттрибута "{metadata.get("name")}":'
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=reply)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    reply = SAC.launch(message.from_user.id, message.text)

    if reply:
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.from_user.id, reply, reply_markup=markup)


bot.infinity_polling(timeout=10, long_polling_timeout=5)
