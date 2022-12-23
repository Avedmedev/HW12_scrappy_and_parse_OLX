import json


def get_url_list(filename: str) -> list:
    with open(filename) as fp:
        url_list = json.load(fp)
    return url_list.get('urls')


def get_url_dict(filename: str) -> dict:
    with open(filename) as fp:
        url_list = json.load(fp)
    return url_list.get('urls')


