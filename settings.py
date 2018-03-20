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
        return self.settings["Token"]

    @property
    def mal_user(self):
        return self.settings["MyAnimeList"]["User"]

    @property
    def mal_pass(self):
        return self.settings["MyAnimeList"]["Pass"]

    @property
    def reddit_client_id(self):
        return self.settings["Reddit"]["Client-ID"]

    @property
    def reddit_client_secret(self):
        return self.settings["Reddit"]["Client-Secret"]

    @property
    def league_api_key(self):
        return self.settings["League"]