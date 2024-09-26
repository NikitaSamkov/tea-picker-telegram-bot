import os.path
from configparser import ConfigParser
import telebot

from constants import Constants
from crud import create_tea, delete_tea, all_tea, random_tea, create_wisdom, add_cup
from statistics import get_statistics, generate_graph
from settings import init_settings

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


@bot.message_handler(commands=['add_tea'])
def add_tea(message):
    reply = create_tea(message)
    bot.send_message(message.from_user.id, reply)


@bot.message_handler(commands=['delete'])
def delete_tea(message):
    reply = delete_tea(message)
    bot.send_message(message.from_user.id, reply)


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
    reply = create_wisdom(message)
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
    generate_graph(message, config)
    with open(os.path.join(Constants.USER_DIR, f'{message.from_user.id}.png'), 'rb') as photo:
        bot.send_photo(message.from_user.id, photo)


bot.polling(none_stop=True, interval=0, timeout=0)
