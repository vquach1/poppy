import json
import os

from enum import Enum

class Settings:
    defaultPath = '/data/settings.json'

    """Need to fix the way the absolute file path is being created"""
    def __init__(self, path = defaultPath):
        dir = os.path.dirname(__file__)
        self.path = dir + path
        self.settings = self.load_settings()
        pass

    def load_settings(self):
        with open(self.path, 'r') as file:
            return json.load(file)

    @property
    def token(self):
        return self.settings['Token']

    @token.setter
    def token(self, value):
        self.settings['Token'] = value