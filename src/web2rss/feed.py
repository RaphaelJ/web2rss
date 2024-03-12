# Copyright (C) 2024 Raphael Javaux
# raphael@noisycamp.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import hashlib

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import bs4
import dateparser
import requests

from feedgen.feed import FeedGenerator
from requests.exceptions import RequestException

from web2rss.models import Feed


@dataclass
class Item:
    url: Optional[str]
    title: Optional[str]
    date: Optional[str]
    description: Optional[str]


def fetch_feed_items(feed: Feed) -> Optional[List[Item]]:
    """Get all the article items of a given Feed object."""

    try:
        resp = requests.get(feed.url)
        resp.raise_for_status()
        resp.encoding = "utf-8"

        html = resp.text
    except RequestException as e:
        return None

    dom = bs4.BeautifulSoup(html, 'html.parser')

    if __feed_has_required_selectors(feed):
        articles = dom.select(feed.article_selector)

        items = [
            __parse_article(feed, article)
            for article in articles
        ]
        items = [i for i in items if i is not None]
    else:
        items = None

    return items


def feed_to_rss(feed: Feed, items: List[Item]) -> str:
    fg = FeedGenerator()

    fg.id(feed.url)
    fg.link(href="http://127.0.0.1:5000/feed/1.xml", rel="self")
    fg.link(href=feed.url, rel="alternate")
    fg.title(feed.page_title)
    fg.description(f"RSS feed generated from {feed.url}.")

    for item in reversed(items):
        fe = fg.add_entry()

        fe.guid()

        guid_components = []

        if item.url:
            fe.link(href=item.url)
            guid_components.append(item.url)

        if item.title:
            fe.title(item.title)
            guid_components.append(item.title)

        if item.date:
            fe.pubdate(item.date)
            guid_components.append(item.date)

        if item.description:
            fe.content(item.description, type="CDATA")

        fe.guid(__gen_guid(guid_components))

    return fg.rss_str(pretty=True)


def __feed_has_required_selectors(feed: Feed) -> bool:
    return feed.article_selector and any([feed.title_selector, feed.description_selector])


def __parse_article(feed: Feed, article: bs4.element.Tag) -> Optional[Item]:
    url = __parse_url(article, feed.url_selector)
    title = __parse_text(article, feed.title_selector)
    date = __parse_date(article, feed.date_selector)
    desc = __parse_text(article, feed.description_selector)

    if title or desc:  # RSS requires at least one of `title` or `desc`.
        return Item(url, title, date, desc)
    else:
        return None


def __parse_text(article: bs4.element.Tag, selector: str) -> Optional[str]:
    if selector is None:
        return None

    text_tag = article.select_one(selector)

    if text_tag is not None:
        return text_tag.text
    else:
        return None


def __parse_url(article: bs4.element.Tag, selector: str) -> Optional[str]:
    if selector is None:
        return None

    url_tag = article.select_one(selector)

    if url_tag is None:
        return None
    elif "href" in url_tag.attrs:
        return url_tag.attrs["href"]
    elif url_tag.text.startswith(("http://", "https://")):
        return url_tag.text
    else:
        return None


def __parse_date(article: bs4.element.Tag, selector: str) -> Optional[datetime]:
    date_text = __parse_text(article, selector)

    if date_text is not None:
        return dateparser.parse(date_text)
    else:
        return None


def __gen_guid(components: List[str]) -> str:
    """Generates an unique and deterministic ID from an item content."""

    encoded_components = "+".join(components).encode("utf-8")
    return hashlib.sha256(encoded_components).hexdigest()