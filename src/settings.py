import pathlib
from typing import Any

import yaml

BASE_DIR = pathlib.Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = BASE_DIR / 'config' / 'config.yaml'


def load_config(filename=DEFAULT_CONFIG_PATH) -> Any:
    with open(filename, 'rt') as f:
        data = yaml.safe_load(f)
    return data


config = load_config(DEFAULT_CONFIG_PATH)
