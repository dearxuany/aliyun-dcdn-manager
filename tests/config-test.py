#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

import yaml

def load_yaml_conf(confPath):
    yamlFile = open(confPath)
    yamlConf = yaml.load(yamlFile, Loader=yaml.FullLoader)

    return yamlConf


if __name__ == "__main__":
    confPath = "../config/config.yaml"
    print(load_yaml_conf(confPath))
