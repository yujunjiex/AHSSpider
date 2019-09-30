# coding: UTF-8

import logging
import yaml
import logging.config
import os
parent_path = os.path.dirname(os.path.dirname(__file__))+'/'


def setup_logging(default_path='config.yaml', default_level=logging.INFO):
    path = default_path

    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            for _handler in config["handlers"].values():
                for item in _handler:
                    if item == "filename":
                        _handler[item] = parent_path + _handler[item]
            logging.config.dictConfig(config)
            # print("sz", config)
    else:
        logging.basicConfig(level=default_level)




