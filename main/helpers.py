import os
import yaml


def get_config(default_config_path):
    config_path = os.getenv('POCKETBOOK_CONF')
    if (config_path is None
            or not os.path.exists(config_path)):
        config_path = default_config_path

    with open(config_path, 'rt') as config_file:
        config = yaml.load(
            config_file,
            Loader=yaml.FullLoader,
        )
        return config
