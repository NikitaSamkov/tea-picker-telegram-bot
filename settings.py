import os
from configparser import ConfigParser
from datetime import datetime

from constants import Constants


def init_settings():
    settings_tmpl = os.path.join(Constants.SETTINGS_DIR, f'{Constants.SETTINGS_FILE}.template')
    if not os.path.exists(settings_tmpl):
        raise NotImplementedError('Не объявлен шаблон настроек!')
    config_tmpl = ConfigParser()
    config_tmpl.read(settings_tmpl)
    bot_token = input('Введите токен бота: ')
    config_tmpl.set('bot_settings', 'BOT_TOKEN', bot_token)
    admin_id = input('Введите ваш telegram id (посмотреть можно, написав @userinfobot): ')
    config_tmpl.set('admin', 'ADMIN_ID', admin_id)
    with open(os.path.join(Constants.SETTINGS_DIR, Constants.SETTINGS_FILE), 'w') as settings_f:
        config_tmpl.write(settings_f)
    print('Токен сохранён!')


def log(message):
    date = datetime.fromtimestamp(message.date)
    log_dir = os.path.join(Constants.LOG_DIR, str(date.year))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = f'{Constants.str_date(date)}.log'
    path = os.path.join(log_dir, log_file)

    with open(path, 'a', encoding='utf-8') as f:
        msg = f'[{Constants.str_time(date)}] @{message.from_user.username}({message.from_user.id}) - "{message.text}"\n'
        f.write(msg)
