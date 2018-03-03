from base64 import b64encode
import urllib
import requests
from bs4 import *
from mal_parser.media_objects import *

class Mal:
    def __init__(self, user, passw):
        userpass = user + ":" + passw
        auth_value = "Basic " + b64encode(userpass.encode()).decode()
        self.auth_head = {"Authorization": auth_value}

    def search(self, name, media_type):
        name_encoded = urllib.parse.quote(name)
        url = "https://myanimelist.net/api/{}/search.xml?q={}".format(media_type.name, name_encoded)
        result = requests.get(url, headers=self.auth_head)

        soup = BeautifulSoup(result.text, "lxml")
        entry = soup.find("entry")
        if entry is None:
            return None
        else:
            return Anime(entry) if media_type == MediaTypes.anime else Manga(entry)
