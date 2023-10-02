import json


def read_json_list(json_list_file):
    with open(json_list_file) as f:
        item_list = [item for item in json.load(f)]
        print(f'finish read json list file: {json_list_file}, res len: {len(item_list)}.')
        return item_list


def get_location_list(location_file='location_seed.json'):
    return read_json_list(location_file)


def get_title_list(title_file='title_seed.json'):
    return read_json_list(title_file)
