from common import get_data, save_data, get_tea_list, get_file_by_id
from constants import Constants


def get_metadata():
    return get_data(Constants.METADATA_FILE)


def get_tea_meta(tea_data):
    metadata = get_metadata()
    tea_meta = []
    for meta_id, meta_info in metadata.items():
        meta_name = metadata.get(meta_id, {}).get('name', None)
        if not meta_name:
            continue
        tea_meta.append({'id': meta_id, 'name': meta_name, 'value': tea_data.get(meta_id, None)})
    return tea_meta


def get_tea_info(user_id, tea_name):
    tea_list = get_tea_list(get_data(get_file_by_id(user_id)))
    if tea_name not in tea_list:
        return 'Этого чая я не знаю!'
    tea_meta = [f'{item.get("name")}: {item.get("value")}' for item in get_tea_meta(tea_list.get(tea_name, {}))
                if item.get('value', None) is not None]
    reply = f'[{tea_name}]\n\n'
    if len(tea_meta) == 0:
        return reply + 'Это чай.'
    return reply + '\n\n'.join(tea_meta)


def edit_tea_info(user_id, value, tea_name, meta_id):
    user_file = get_file_by_id(user_id)
    data = get_data(user_file)
    tea_list = get_tea_list(data)
    if tea_name not in tea_list:
        return 'О таком чае я ничего не знаю!'
    tea_list[tea_name][meta_id] = value
    save_data(user_file, data)
    return 'Успешно обновлено!'


