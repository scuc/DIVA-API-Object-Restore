#! /usr/bin/env python3

import os
import yaml


def get_config():
    """
    Setup configuration and credentials
    """
    os.chdir("./")
    path = "config.yaml"

    with open(path, "rt") as f:
        config = yaml.safe_load(f.read())

    return config


def ensure_dirs():

    dirs = ["_logs"]

    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)

    return


if __name__ == "__main__":
    get_config()
