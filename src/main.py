import argparse
import json
import logging
import signal
import sys
import time
from pathlib import Path

import requests

from read_rss import parse

flag = True

parser = argparse.ArgumentParser(prog="rss_reader",
                                 description="Subscribe to RSS feeds and download torrents automatically")

parser.add_argument("config_file",
                    type=Path,
                    help="path of config file")


def signal_handler(_, __):
    global flag
    flag = False
    print("Good bye!")
    sys.exit(0)


def download_torrents(url: str, title: str, output: Path):
    response = requests.get(url)
    if response.status_code == 200:
        (output / f"{url.split('/')[-1]}").write_bytes(response.content)
        logging.info(f"Download {title} finished")
    else:
        logging.error(f"Get {title} {url} failed, status code {response.status_code}")


def loop(config: dict):
    before = config["before"]
    output = Path(config["output"])
    if not output.exists():
        logging.error(f"{output} not exist")
        sys.exit(-1)
    while flag:
        results = parse(
            config["subscription"],
            before,
            config["filters"]
        )
        before = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        logging.info(f"update, {len(results)} new torrents")
        for result in results:
            download_torrents(result.torrent_url, result.title, output)
        time.sleep(int(config["update_interval"]))


def main():
    logging.basicConfig(format="%(asctime)s-%(levelname)s: %(message)s", level=logging.WARNING)
    signal.signal(signal.SIGINT, signal_handler)
    args = parser.parse_args()
    config = json.loads(args.config_file.read_text("utf-8"))
    loop(config)
