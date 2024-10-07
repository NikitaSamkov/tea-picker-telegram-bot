import os.path

from datetime import datetime
from common import save_data, get_data
from constants import Constants


TUTORIAL = [
    'Добро пожаловать в демо-режим!',
]


def activate_demo(user_id, demo_name):
    demo_path = os.path.join(Constants.DEMO_DIR, f'{demo_name}.json')
    if not os.path.exists(demo_path):
        return 'Выбранного демо не существует!'
    demo_data = get_data(demo_path)

    demo_stats = demo_data.get(Constants.STATS_KEY, {})
    dates = list(map(Constants.get_date_from_str, demo_stats.keys()))
    dates.sort()
    td = datetime.now() - max(dates)
    demo_stats = {Constants.str_date(item + td): demo_stats.get(Constants.str_date(item), []) for item in dates}
    demo_data[Constants.STATS_KEY] = demo_stats

    save_data(os.path.join(Constants.USER_DIR, f'{user_id}.json'), demo_data)
    return '\n\n'.join(TUTORIAL)

