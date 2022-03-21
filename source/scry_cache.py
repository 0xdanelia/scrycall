import json
import hashlib
import re
import pathlib
from abc import ABCMeta, abstractmethod
from typing import Any


class Cache(metaclass=ABCMeta):
    def __init__(self, path: pathlib.Path):
        self.path = path
        if not self.path.is_dir():
            self.path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def uid(cls, item: Any) -> str:
        """Unique ID for the item

        Args:
            item: Item name

        Returns:
            str: unique ID
        """

    def _write_content_to_file(self, path, data):
        with open(path, "w") as cachefile:
            json.dump(data, cachefile, indent=4)

    def _read_from_file(self, path):
        try:
            with open(path, "r") as cachefile:
                return json.load(cachefile)
        except:
            return None

    def load_item(self, uid: str):
        """Load item by its unique id

        Args:
            uid: Unique ID
        """
        path = self.path / uid
        return self._read_from_file(path)


class UrlCardCache(Cache):
    """Store lists of Card cache IDs"""

    def __init__(self):
        super().__init__(pathlib.Path.home() / ".cache/scrycall/api/")

    @classmethod
    def uid(cls, url) -> str:
        return hashlib.md5(url.encode()).hexdigest()

    def store_url(self, url, cards: list[dict]):
        path = self.path / self.uid(url)
        ids = [CardCache.uid(card) for card in cards]
        self._write_content_to_file(path, ids)


class CardCache(Cache):
    def __init__(self):
        super().__init__(pathlib.Path.home() / ".cache/scrycall/card/")

    @classmethod
    def uid(cls, card: dict) -> str:
        name = card["name"].replace(" ", "_")
        name = re.sub("[^a-zA-Z0-9_]", "-", name)
        return f"{name}_{card['id']}"

    def store_card(self, card: dict):
        path = self.path / self.uid(card)
        self._write_content_to_file(path, card)
