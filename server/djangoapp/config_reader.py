import json
import os

class ConfigReader:
    """ singleton class to read config file"""
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if ConfigReader.__instance == None:
            ConfigReader()
        return ConfigReader.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if ConfigReader.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            ConfigReader.__instance = self

    def read_config(self):
        this_file_dir = os.path.dirname(__file__)
        file_path = os.path.join(this_file_dir, 'config.json')
        with open(file_path, 'r') as f:
            config = json.load(f)
        return config