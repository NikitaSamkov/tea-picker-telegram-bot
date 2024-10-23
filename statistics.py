import os
from datetime import timedelta, datetime
from matplotlib import pyplot as plt
import matplotlib.dates as matplotlib_dates
import locale
import calendar

from common import get_data, get_user_file, get_file_by_id
from constants import Constants


locale.setlocale(locale.LC_ALL, 'ru_RU')
plt.switch_backend('agg')


def get_statistics(message):
    reply = '========================\nСТАТИСТИКА\n========================\n\n'
    data = get_data(get_user_file(message))
    stats = data.get(Constants.STATS_KEY, {})
    cur_date = Constants.get_date()
    cups = len(stats.get(cur_date, []))
    all_teabags = sum([int(item.get('teabags', Constants.TEABAGS_COUNT))
                       for item in data.get(Constants.TEA_KEY, {}).values()])
    picked_tea = [(key, value.get('picked', None)) for key, value in data.get(Constants.TEA_KEY, {}).items()
                  if value.get('picked', None) is not None]
    stat_parts = [
        f'За сегодня ты выпил {cups} кружек чая.',
        f'А это, на секунду, {cups * Constants.CUP_ML}мл чая!',
        f'Кроме того, это {(cups * Constants.CUP_ML * 100) // Constants.NEEDED_ML}% от суточной нормы воды!',
        f'Если ты продолжишь в том же духе, то чая тебе хватит максимум на '
        f'{max(all_teabags // (cups or 1) - 1, 0)} дней!',
        f'А если каждый пакетик заваривать дважды, то максимум на '
        f'{max(all_teabags // ((cups or 1) // 2 or 1) - 1, 0)} дней!'
    ]
    if len(picked_tea) > 0:
        stat_parts.append(f'Кстати, мой любимый чай - это {max(picked_tea, key=lambda item: item[1])[0]}!')

    reply = reply + '\n'.join(stat_parts)
    prev_reaction = ''
    for needed_cups, reaction in Constants.STATS_REACTIONS.items():
        if needed_cups > cups:
            break
        prev_reaction = reaction
    reply = reply + '\n\n' + prev_reaction
    return reply


def calculate_tea_speed(cups_timestaps):
    if len(cups_timestaps) == 0:
        return []
    cups_time = []
    cups_speed = []
    for i in range(len(cups_timestaps) - 1):
        cur_time = Constants.get_time_from_str(cups_timestaps[i])
        cups_time.append(cur_time)
        time_diff = Constants.get_time_from_str(cups_timestaps[i + 1]) - cur_time
        hours = (time_diff.total_seconds() or 1) / 3600
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
            return max(values) * multiplier or 1
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
    axis.set_title('Скорость питья чая за день', color=text_color)
    cups = stats.get(cur_date, [])
    if len(cups) < 2:
        times = ['09:00:00', '18:00:00']
        cups_time, cups_speed = [Constants.get_time_from_str(item) for item in times], [0, 0]
    else:
        cups_time, cups_speed = calculate_tea_speed(cups)
    marker = 'o' if len(cups_speed) == 1 else None
    set_subplot_bg(axis, cups_time, cups_speed, config)
    axis.plot(cups_time, cups_speed, color=graph_line_color, linewidth=3, marker=marker)
    axis.set_xlabel('Время', color=text_color)
    axis.set_ylabel('Скорость (кружек в час)', color=text_color)
    axis.tick_params(axis='x', rotation=45, colors=text_color)
    axis.tick_params(axis='y', colors=text_color)
    axis.xaxis.set_major_formatter(matplotlib_dates.DateFormatter('%H:%M'))


def set_today_count_graph(stats, axis, text_color, graph_line_color, cur_date, config):
    axis.set_title('Количество выпитого чая за день', color=text_color)
    cups = stats.get(cur_date, [])
    if len(cups) < 1:
        times = ['09:00:00', '18:00:00']
        cups_time, cups_count = [Constants.get_time_from_str(item) for item in times], [0, 0]
    else:
        cups_time = list(map(Constants.get_time_from_str, cups))
        cups_count = [i + 1 for i in range(len(cups))]
    marker = 'o' if len(cups_count) == 1 else None
    set_subplot_bg(axis, cups_time, cups_count, config)
    axis.plot(cups_time, cups_count, color=graph_line_color, linewidth=3, marker=marker)
    axis.set_xlabel('Время', color=text_color)
    axis.set_ylabel('Количество кружек', color=text_color)
    axis.tick_params(axis='x', rotation=45, colors=text_color)
    axis.tick_params(axis='y', colors=text_color)
    axis.xaxis.set_major_formatter(matplotlib_dates.DateFormatter('%H:%M'))


def get_graph_period(start_date, stats):
    past = []
    now = Constants.get_date_from_str(start_date)
    future = []
    to_add_past = 0
    to_add_future = 0
    keys = list(map(Constants.get_date_from_str, stats.keys()))
    limit_past = min(keys)
    limit_future = max(keys)

    for i in range(Constants.GRAPH_MAX_DAYS):
        td = timedelta(days=(i + 1))
        if now - td >= limit_past:
            past.append(now - td)
        else:
            to_add_future += 1
        if now + td <= limit_future:
            future.append(now + td)
        else:
            to_add_past += 1
    for i in range(to_add_past):
        td = timedelta(days=(Constants.GRAPH_MAX_DAYS + i + 1))
        if now - td < limit_past:
            break
        past.append(now - td)
    for i in range(to_add_future):
        td = timedelta(days=(Constants.GRAPH_MAX_DAYS + i + 1))
        if now + td > limit_future:
            break
        future.append(now + td)
    past.reverse()
    return past + [now] + future


def set_daily_count_graph(stats, axis, text_color, graph_line_color, cur_date, config):
    axis.set_title('Количество кружек чая по дням', color=text_color)
    if len(stats) < 2:
        return
    period = get_graph_period(cur_date, stats)
    counts = [len(stats.get(Constants.str_date(item), [])) for item in period]
    set_subplot_bg(axis, period, counts, config)
    axis.plot(period, counts, color=graph_line_color, linewidth=3)
    axis.set_xlabel('Дата', color=text_color)
    axis.set_ylabel('Кружки', color=text_color)
    axis.tick_params(axis='x', colors=text_color, rotation=45)
    axis.tick_params(axis='y', colors=text_color)
    axis.xaxis.set_major_formatter(matplotlib_dates.DateFormatter('%d-%m-%Y'))


def set_daily_speed_graph(stats, axis, text_color, graph_line_color, cur_date, config):
    axis.set_title('Средняя скорость питья чая по дням', color=text_color)
    if len(stats) < 2:
        return
    period = get_graph_period(cur_date, stats)
    dates = []
    mid_speed = []
    for date in period:
        dates.append(date)
        timestamps = stats.get(Constants.str_date(date), [])
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
    set_daily_speed_graph(stats, axs[1, 0], text_color, graph_line_color, date, config)
    set_daily_count_graph(stats, axs[1, 1], text_color, graph_line_color, date, config)

    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)

    plt.tight_layout()
    plt.savefig(os.path.join(Constants.USER_DIR, f'{user_id}.png'))


def get_cup_time(cups_timestamps: list):
    result = []
    timestamps = list(map(Constants.get_time_from_str, cups_timestamps))
    for i in range(len(timestamps) - 1):
        result.append(timestamps[i + 1] - timestamps[i])
    return result


def get_work_time(cups_timestamps: list):
    if len(cups_timestamps) == 0:
        return timedelta()
    if len(cups_timestamps) == 1:
        return Constants.AVERAGE_TEA_TIME
    cup_times = get_cup_time(cups_timestamps)
    cup_times.append(sum(cup_times, timedelta()) / len(cup_times))
    return sum(cup_times, timedelta())


def get_week_stats(message):
    reply = '========================\nСТАТИСТИКА НЕДЕЛИ\n========================\n\n'
    data = get_data(get_user_file(message))
    stats = data.get(Constants.STATS_KEY, {})
    day_names = list(map(lambda item: item.upper(), calendar.day_name))
    today = datetime.today()
    cur_day_of_week = today.isoweekday()
    week = [Constants.str_date(today + timedelta(days=i)) for i in range(1 - cur_day_of_week, 7 - cur_day_of_week + 1)]

    stat_parts = []
    total_cups = 0
    best_mid_speed = (0, 0)
    best_cups = (0, 0)
    hot_time = None
    longest_day = (timedelta(seconds=0), 0)
    shortest_day = (timedelta(hours=24), 0)

    for i, date in enumerate(week):
        timestamps = stats.get(date, [])
        total_cups += len(timestamps)
        if len(timestamps) > 1:
            _, speed = calculate_tea_speed(timestamps)
            cups_time = list(map(Constants.get_time_from_str, timestamps))
            mid_speed = round(sum(speed) / len(speed), 3)
            if mid_speed > best_mid_speed[0]:
                best_mid_speed = (mid_speed, i)
            hot_idx = speed.index(max(speed))
            hot_period = (cups_time[hot_idx], cups_time[hot_idx + 1])
            if hot_time is None:
                hot_time = hot_period
            elif (hot_time[0] <= hot_period[0] < hot_time[1]) or (hot_time[0] < hot_period[1] <= hot_time[1]):
                hot_time = (max(hot_time[0], hot_period[0]), min(hot_time[1], hot_period[1]))
            else:
                hot_time = (min(hot_time[0], hot_period[0]), max(hot_time[1], hot_period[1]))
            work_time = get_work_time(timestamps)
            if work_time > longest_day[0]:
                longest_day = (work_time, i)
            if work_time < shortest_day[0]:
                shortest_day = (work_time, i)
        if len(timestamps) > best_cups[0]:
            best_cups = (len(timestamps), i)


    stat_parts.append(f'За эту неделю было выпито {(total_cups * Constants.CUP_ML) / 1000} литров чая.')
    stat_parts.append(f'Если считать, что налить чай ты ходишь 5 минут, '
                      f'то ты потратил на этой неделе ~{round(total_cups * 5 / 60, 1)} часов на это.')
    stat_parts.append(f'Самый скоростной день недели - {day_names[best_mid_speed[1]]}. '
                      f'Скорость была {best_mid_speed[0]} кружек в час.')
    stat_parts.append(f'Чайный день - {day_names[best_cups[1]]}. Было выпито {best_cups[0]} кружек чая!')
    if hot_time is not None:
        stat_parts.append(f'Самые горячие часы за неделю: '
                          f'{hot_time[0].strftime("%H:%M")}-{hot_time[1].strftime("%H:%M")}'
                          f'\nВ этот период скорость была на высочайшем уровне!')
    longest_day_date = datetime(day=1, month=1, year=2024) + longest_day[0]
    shortest_day_date = datetime(day=1, month=1, year=2024) + shortest_day[0]
    stat_parts.append(f'Дольше всего ты работал в {day_names[longest_day[1]]} '
                      f'(~{longest_day_date.hour} часов и {longest_day_date.minute} минут)!')
    stat_parts.append(f'А вот меньше всего ты работал в {day_names[shortest_day[1]]} '
                      f'(~{shortest_day_date.hour} часов и {shortest_day_date.minute} минут)!')

    reply = reply + '\n\n'.join(stat_parts)
    return reply
