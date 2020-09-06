import json
import os
import re
from itertools import (
    chain,
)
from typing import (
    Any,
    Dict,
    Iterable,
    Iterator,
    Optional,
    Tuple,
)

import yaml


def _parse_config(path: str) -> Dict[str, Any]:
    with open(path, 'rt', encoding='utf-8') as config_file:
        if path.endswith('json'):
            config = json.load(config_file)
        elif path.endswith(('yaml', 'yml')):
            config = yaml.load(
                config_file,
                Loader=yaml.FullLoader,
            )
        else:
            raise ValueError('Unknown config-file extension!')

    return config


def _get_first_existing_config(paths: Iterable[str]) -> Dict[str, Any]:
    config: Optional[Dict[str, Any]] = None

    for path in paths:
        if not os.path.exists(path):
            continue

        config = _parse_config(path)
        break

    if config is None:
        raise ValueError('Config is None!')

    return config


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

    return _get_first_existing_config(config_paths)


_SINGLE_NUMBER_REGEXP = r'(?:0|[1-9]\d*)'
_VERSION_REGEXP = re.compile(
    pattern='(?:{number}\\.){{2}}{number}'.format(
        number=_SINGLE_NUMBER_REGEXP,
    )
)


def _validate_version(config: Dict[str, Any], name: str) -> None:
    if 'version' not in config:
        raise ValueError(f"Missing '{name}' version of the project!")

    version_value = config['version']
    if not isinstance(version_value, str):
        raise ValueError(f"Value of '{name}' version must be a string!")

    match = _VERSION_REGEXP.match(version_value)
    if match is None:
        raise ValueError(f"Value of '{name}' version must be like 'number.number.number' where 'number' is an integer without leading zeros!")  # noqa


def _validate_version_config(config: Dict[str, Any]) -> None:
    if not all(isinstance(key, str) for key in config):
        raise ValueError('All keys must be a strings!')

    _validate_version(config, 'main')

    subversions: Tuple[str, ...] = (
        'data_model',
        'api_model',
    )

    for name in subversions:
        try:
            subconfig = config[name]

            if not isinstance(subconfig, dict):
                raise ValueError(f"The '{name}' subconfig must be a dictionary!")  # noqa

            if not all(isinstance(key, str) for key in subconfig):
                raise ValueError(f"Keys of '{name}' subconfig must be strings!")  # noqa

            _validate_version(subconfig, name)
        except KeyError:
            raise ValueError(f"Version of '{name}' expected in version config!")  # noqa


def get_version_config() -> Dict[str, Any]:
    names_to_check: Tuple[str, ...] = (
        'version_conf.json',
        'version_conf.yaml',
    )

    location: str = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
    ))

    paths: Iterator[str] = (
        os.path.join(
            location,
            name,
        )
        for name in names_to_check
    )

    config: Dict[str, Any]
    config = _get_first_existing_config(paths)

    _validate_version_config(config)

    return config


def get_version() -> str:
    return get_version_config()['version']


def get_data_model_version() -> str:
    return get_version_config()['data_model']['version']
