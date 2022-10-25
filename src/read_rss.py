import re
import time
from typing import NamedTuple

import feedparser


class Result(NamedTuple):
    title: str
    torrent_url: str


def parse(url: str, before: str, filters: list[str]):
    results = []
    before_time = time.strptime(before, "%Y-%m-%dT%H:%M:%S")
    before_seconds = time.mktime(before_time)
    d = feedparser.parse(url)
    for entry in d.entries:
        published_seconds = time.mktime(entry["published_parsed"])
        if published_seconds >= before_seconds and any([re.match(f, entry["title"]) for f in filters]):
            for link in entry["links"]:
                if link["type"] == "application/x-bittorrent":
                    results.append(Result(entry["title"], link["href"]))
    return results
