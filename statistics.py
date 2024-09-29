import os
from datetime import timedelta, datetime
from matplotlib import pyplot as plt
import matplotlib.dates as matplotlib_dates

from common import get_data, get_user_file, get_file_by_id
from constants import Constants


plt.switch_backend('agg')


def get_statistics(message):
    reply = '========================\nСТАТИСТИКА\n========================\n\n'
    data = get_data(get_user_file(message))
    stats = data.get(Constants.STATS_KEY, {})
    cur_date = Constants.get_date()
    cups = len(stats.get(cur_date, []))
    stat_parts = [
        f'За сегодня ты выпил {cups} кружек чая.',
        f'А это, на секунду, {cups * Constants.CUP_ML}мл чая!',
        f'Кроме того, это {(cups * Constants.CUP_ML * 100) // Constants.NEEDED_ML}% от суточной нормы воды!',
        f'Если вы продолжите в том же духе, то чая вам хватит максимум на '
        f'{max((len(data.get(Constants.TEA_KEY, [])) * Constants.TEABAGS_COUNT) // cups - 1, 0)} дней!',
    ]
    reply = reply + '\n'.join(stat_parts)
    prev_reaction = ''
    for needed_cups, reaction in Constants.STATS_REACTIONS.items():
        if needed_cups > cups:
            break
        prev_reaction = reaction
    reply = reply + '\n\n' + prev_reaction
    return reply


def calculate_tea_speed(cups_timestaps):
    cups_time = []
    cups_speed = []
    for i in range(len(cups_timestaps) - 1):
        cur_time = Constants.get_time_from_str(cups_timestaps[i])
        cups_time.append(cur_time)
        time_diff = Constants.get_time_from_str(cups_timestaps[i + 1]) - cur_time
        hours = time_diff.total_seconds() / 3600
        cups_speed.append(round(1 / hours, 2))
    return cups_time, cups_speed


def set_subplot_bg(axis, data_x, data_y, config):
    def get_margin(values):
        multiplier = 0.1
        line = max(values) - min(values)
        if isinstance(line, timedelta):
            if line.total_seconds() == 0:
                return timedelta(minutes=15)
            return timedelta(seconds=line.total_seconds() * multiplier)
        if line == 0:
            return max(values) * multiplier
        return line * multiplier

    res_dir = config.get('customization', 'RES_DIR', fallback=None)
    bg = config.get('customization', 'SUBPLOT_BG', fallback=None)
    if not bg or not res_dir:
        return
    image = plt.imread(os.path.join(res_dir, bg))
    margin_x = get_margin(data_x)
    margin_y = get_margin(data_y)

    extent = [min(data_x) - margin_x, max(data_x) + margin_x, min(data_y) - margin_y, max(data_y) + margin_y]
    axis.imshow(image, extent=extent, aspect='auto', zorder=-1)
    edge_color = config.get('customization', 'EDGE_COLOR', fallback=None)
    if edge_color:
        for spine in axis.spines.values():
            spine.set_edgecolor(edge_color)


def set_today_speed_graph(stats, axis, text_color, graph_line_color, cur_date, config):
    axis.set_title('Скорость питья чая за сегодня', color=text_color)
    cups = stats.get(cur_date, [])
    if len(cups) < 2:
        return
    cups_time, cups_speed = calculate_tea_speed(cups)
    set_subplot_bg(axis, cups_time, cups_speed, config)
    axis.plot(cups_time, cups_speed, color=graph_line_color, linewidth=3)
    axis.set_xlabel('Время', color=text_color)
    axis.set_ylabel('Скорость (кружек в час)', color=text_color)
    axis.tick_params(axis='x', colors=text_color)
    axis.tick_params(axis='y', colors=text_color)
    axis.xaxis.set_major_formatter(matplotlib_dates.DateFormatter('%H:%M'))


def set_today_count_graph(stats, axis, text_color, graph_line_color, cur_date, config):
    axis.set_title('Количество выпитого чая за сегодня', color=text_color)
    cups = stats.get(cur_date, [])
    if len(cups) < 2:
        return
    cups_time = list(map(Constants.get_time_from_str, cups))
    cups_count = [i + 1 for i in range(len(cups))]
    set_subplot_bg(axis, cups_time, cups_count, config)
    axis.plot(cups_time, cups_count, color=graph_line_color, linewidth=3)
    axis.set_xlabel('Время', color=text_color)
    axis.set_ylabel('Количество кружек', color=text_color)
    axis.tick_params(axis='x', colors=text_color)
    axis.tick_params(axis='y', colors=text_color)
    axis.xaxis.set_major_formatter(matplotlib_dates.DateFormatter('%H:%M'))


def set_daily_count_graph(stats, axis, text_color, graph_line_color, config):
    axis.set_title('Количество кружек чая по дням', color=text_color)
    if len(stats) < 2:
        return
    dates = [Constants.get_date_from_str(item) for item in list(stats.keys())[-Constants.GRAPH_MAX_DAYS:]]
    counts = [len(item) for item in list(stats.values())[-Constants.GRAPH_MAX_DAYS:]]
    set_subplot_bg(axis, dates, counts, config)
    axis.plot(dates, counts, color=graph_line_color, linewidth=3)
    axis.set_xlabel('Дата', color=text_color)
    axis.set_ylabel('Кружки', color=text_color)
    axis.tick_params(axis='x', colors=text_color, rotation=45)
    axis.tick_params(axis='y', colors=text_color)
    axis.xaxis.set_major_formatter(matplotlib_dates.DateFormatter('%d-%m-%Y'))


def set_daily_speed_graph(stats, axis, text_color, graph_line_color, config):
    axis.set_title('Средняя скорость питья чая по дням', color=text_color)
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
    set_subplot_bg(axis, dates, mid_speed, config)
    axis.plot(dates, mid_speed, color=graph_line_color, linewidth=3)
    axis.set_xlabel('Дата', color=text_color)
    axis.set_ylabel('Средняя скорость (кружек в час)', color=text_color)
    axis.tick_params(axis='x', colors=text_color, rotation=45)
    axis.tick_params(axis='y', colors=text_color)
    axis.xaxis.set_major_formatter(matplotlib_dates.DateFormatter('%d-%m-%Y'))


def generate_graph(user_id, date, config):
    try:
        date = datetime.strptime(date, '%d.%m.%Y').strftime('%d-%m-%Y') if date else Constants.get_date()
    except:
        date = Constants.get_date()

    text_color = config.get('customization', 'TEXT_COLOR', fallback='black')
    graph_line_color = config.get('customization', 'GRAPH_LINE_COLOR', fallback='blue')

    data = get_data(get_file_by_id(user_id))
    stats = data.get(Constants.STATS_KEY, {})

    plt.clf()
    plt.title('Статистика чая', color=text_color)
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))
    bg = config.get('customization', 'PLOT_BG', fallback=None)
    res_dir = config.get('customization', 'RES_DIR', fallback=None)
    if bg and res_dir:
        fig.figimage(plt.imread(os.path.join(res_dir, bg)), xo=0, yo=0, zorder=-1)

    set_today_speed_graph(stats, axs[0, 0], text_color, graph_line_color, date, config)
    set_today_count_graph(stats, axs[0, 1], text_color, graph_line_color, date, config)
    set_daily_speed_graph(stats, axs[1, 0], text_color, graph_line_color, config)
    set_daily_count_graph(stats, axs[1, 1], text_color, graph_line_color, config)

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    plt.tight_layout()
    plt.savefig(os.path.join(Constants.USER_DIR, f'{user_id}.png'))
