import html
import re
from enum import Enum

class MediaTypes(Enum):
    anime = 1
    manga = 2

class Media:
    def __init__(self, bs_entry):
        self.id = bs_entry.id.text
        self.title = bs_entry.title.text
        self.english = bs_entry.english.text
        self.synonyms = bs_entry.synonyms.text
        self.score = bs_entry.score.text
        self.type = bs_entry.type.text
        self.status = bs_entry.status.text
        self.start_date = bs_entry.start_date.text
        self.end_date = bs_entry.end_date.text
        self.synopsis = self._clean_synopsis(bs_entry.synopsis.text)
        self.image = bs_entry.image.text

    def truncate_synopsis(self, maxlen=1000):
        if maxlen <= 3:
            raise ValueError("The truncated synopsis must have at least 4 characters")

        if len(self.synopsis) <= maxlen:
            return self.synopsis
        else:
            return self.synopsis[0:maxlen-4] + "..."

    def _clean_synopsis(self, text):
        text = html.unescape(text)
        text = text.replace("<br />", "")
        text = re.sub("\[\/?i\]", "_", text)
        return text


class Anime(Media):
    def __init__(self, bs_entry):
        super().__init__(bs_entry)
        self.episodes = bs_entry.episodes.text
        self.link = "https://myanimelist.net/anime/" + self.id


class Manga(Media):
    def __init__(self, bs_entry):
        super().__init__(bs_entry)
        self.chapters = bs_entry.chapters.text
        self.volumes = bs_entry.volumes.text
        self.link = "https://myanimelist.net/manga/" + self.id