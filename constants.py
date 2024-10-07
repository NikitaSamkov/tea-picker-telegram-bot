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
    GRAPH_MAX_DAYS = 14
    TEABAGS_COUNT = 25
    DATE_FORMAT = '%d-%m-%Y'
    METADATA_FILE = 'available_metadata.json'
    MARK_SYMBOL = '✅'
    CROSS_SYMBOL = '❌'
    DEMO_DIR = 'demo'

    @staticmethod
    def get_date():
        return datetime.today().strftime(Constants.DATE_FORMAT)

    @staticmethod
    def str_date(date):
        return date.strftime(Constants.DATE_FORMAT)

    @staticmethod
    def get_date_from_str(str_date: str):
        return datetime.strptime(str_date, Constants.DATE_FORMAT)

    @staticmethod
    def get_time():
        return datetime.now().strftime('%H:%M:%S')

    @staticmethod
    def get_time_from_str(str_time: str):
        return datetime.strptime(str_time, '%H:%M:%S')
