from datetime import datetime


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