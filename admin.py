import os
from common import get_data
from constants import Constants


def clear_empty_records():
    count = 0
    for item in os.listdir(Constants.USER_DIR):
        path = os.path.join(Constants.USER_DIR, item)
        if item.endswith('.json') and os.path.isfile(path):
            print(f'Проверяю {item}')
            try:
                data = get_data(path)
            except Exception:
                data = {}
            if Constants.INFO_KEY in data:
                data.pop(Constants.INFO_KEY)
            if len(data) == 0:
                print(f'Удаляю')
                os.remove(path)
                count += 1
    return f'Удалено {count} записей'


def clear_old_records():
    count = 0
    for item in os.listdir(Constants.USER_DIR):
        path = os.path.join(Constants.USER_DIR, item)
        if item.endswith('.json') and os.path.isfile(path):
            print(f'Проверяю {item}')
            data = get_data(path)
            if Constants.STATS_KEY not in data or len(data.get(Constants.STATS_KEY, {})) == 0:
                os.remove(path)
                count += 1
                continue
            stats: dict = data.get(Constants.STATS_KEY)
            last_day = max(stats.keys(), key=Constants.get_date_from_str)
            print(f'Последний день: {last_day}')
            days_diff = (Constants.get_date_from_str(Constants.get_date()) - Constants.get_date_from_str(last_day)).days
            print(f'Разница: {days_diff} дней')
            if days_diff > 30:
                print('Удаляю')
                os.remove(path)
                count += 1

    return f'Удалено {count} записей'


def clear_png():
    count = 0
    for item in os.listdir(Constants.USER_DIR):
        path = os.path.join(Constants.USER_DIR, item)
        if item.endswith('.png') and os.path.isfile(path):
            print(f'Удаляю {item}')
            os.remove(path)
            count += 1
    return f'Удалено {count} изображений'
