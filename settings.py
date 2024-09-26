import os
from configparser import ConfigParser

from constants import Constants


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