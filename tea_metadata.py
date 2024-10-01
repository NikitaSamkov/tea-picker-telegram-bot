from common import get_data
from constants import Constants


def convert_data(data):
    new_data = {key: {} for key in data}
    return new_data


def get_metadata():
    return get_data(Constants.METADATA_FILE)

