import json
import os
from itertools import (
    chain,
)
from typing import (
    Any,
    Dict,
    Iterator,
    Optional,
)

import yaml


def get_config(config_paths: Iterator[str]) -> Dict[str, Any]:
    custom_config_path: Optional[str] = os.getenv('POCKETBOOK_CONF')

    config_paths: Iterator[str] = filter(
        None,
        chain(
            (
                custom_config_path,
            ),
            config_paths,
        ),
    )

    config: Optional[Dict[str, Any]] = None

    for path in config_paths:
        if not os.path.exists(path):
            continue

        with open(path, 'rt') as config_file:
            if path.endswith('json'):
                config = json.load(config_file)
            elif path.endswith(('yaml', 'yml')):
                config = yaml.load(
                    config_file,
                    Loader=yaml.FullLoader,
                )
            else:
                raise ValueError('Unknown config-file extension!')
        break

    if config is None:
        raise ValueError('Config is None!')

    return config
