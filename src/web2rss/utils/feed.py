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
import os.path

from dataclasses import dataclass
from datetime import datetime, timezone
from functools import cache
from typing import List, Optional
from urllib.parse import urlparse

import bs4
import dateparser
import json
import requests

from feedgen.feed import FeedGenerator
from mistralai.client import MistralClient
from mistralai.exceptions import MistralAPIException
from mistralai.models.chat_completion import ChatMessage
from requests.exceptions import RequestException

from web2rss.app import app
from web2rss.models import Feed


@dataclass
class Article:
    link: Optional[str]
    title: Optional[str]
    date: Optional[str]
    author: Optional[str]
    summary: Optional[str]


def create_feed_from_url(url: str) -> Optional[Feed]:
    dom = _fetch_dom(url)

    if dom is None:
        return None

    page_title_element = dom.select_one("html head title")

    if page_title_element is not None:
        page_title = page_title_element.text
    else:
        page_title = url

    feed = Feed(url=url, page_title=page_title)

    _guess_feed_selectors_from_dom(dom, feed)

    return feed


def fetch_feed_items(feed: Feed) -> Optional[List[Article]]:
    """Get all the article of a given Feed object."""

    dom = _fetch_dom(feed.url)

    if feed.has_required_selectors():
        articles = dom.select(feed.article_selector)

        items = [
            __parse_article_dom(feed, article_dom)
            for article_dom in articles
        ]
        items = [i for i in items if i is not None]
    else:
        items = None

    return items


def feed_to_rss(feed: Feed, items: List[Article]) -> str:
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

        if item.link:
            fe.link(href=item.link)
            guid_components.append(item.link)

        if item.title:
            fe.title(item.title)
            guid_components.append(item.title)

        if item.date:
            fe.pubDate(item.date)
            guid_components.append(str(item.date))

        if item.author:
            # FIXME: RSS requires an email value. Adds a placeholder for now.
            fe.author({"name": item.author, "email": "unknown@domain.tld"})

        if item.summary:
            fe.content(item.summary, type="CDATA")

        fe.guid(__gen_guid(guid_components))

    return fg.rss_str(pretty=True)

def _fetch_dom(url: str) -> Optional[bs4.BeautifulSoup]:
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        resp.encoding = "utf-8"

        html = resp.text
    except RequestException as _e:
        return None

    return bs4.BeautifulSoup(html, "html.parser")


@cache
def _mistral_client() -> MistralClient:
    api_key = app.config["MISTRAL_API_KEY"]
    return MistralClient(api_key)


@cache
def _guess_selectors_prompt() -> str:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    prompt_path = os.path.join(current_dir, "..", "prompts", "guess_selectors.md")

    with open(prompt_path) as f:
        return f.read()


def _guess_feed_selectors_from_dom(dom: bs4.BeautifulSoup, feed: Feed) -> None:
    """Uses a LLM to guess and set the item selectors from the page HTML content."""

    messages = [
        ChatMessage(role="system", content=_guess_selectors_prompt()),
        ChatMessage(role="user", content=str(dom.select_one("body"))),
    ]

    try:
        response = _mistral_client().chat(
            model="mistral-large-latest",
            response_format={"type": "json_object"},
            messages=messages,
        )
    except MistralAPIException:
        return

    try:
        json_response = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return

    if "article" in json_response:
        feed.article_selector = json_response["article"]

        feed.link_selector = json_response.get("link")
        feed.title_selector = json_response.get("title")
        feed.date_selector = json_response.get("date")
        feed.author_selector = json_response.get("author")
        feed.summary_selector = json_response.get("summary")


def __parse_article_dom(feed: Feed, article_dom: bs4.element.Tag) -> Optional[Article]:
    link = __parse_url(feed.url, article_dom, feed.link_selector)
    title = __parse_text(article_dom, feed.title_selector)
    date = __parse_date(article_dom, feed.date_selector)
    author = __parse_text(article_dom, feed.author_selector)
    desc = __parse_text(article_dom, feed.summary_selector)

    if title or desc:  # RSS requires at least one of `title` or `desc`.
        return Article(link, title, date, author, desc)
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


def __parse_url(feed_url: str, article: bs4.element.Tag, selector: str) -> Optional[str]:
    if selector is None:
        return None

    url_tag = article.select_one(selector)

    if url_tag is None:
        return None
    elif "href" in url_tag.attrs:
        return __as_absolute_url(feed_url, url_tag.attrs["href"])
    elif url_tag.text.startswith(("http://", "https://")):
        return __as_absolute_url(feed_url, url_tag.text)
    else:
        return None


def __parse_date(article: bs4.element.Tag, selector: str) -> Optional[datetime]:
    date_text = __parse_text(article, selector)

    if date_text is not None:
        date = dateparser.parse(date_text)

        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)

        return date
    else:
        return None


def __gen_guid(components: List[str]) -> str:
    """Generates an unique and deterministic ID from an item content."""

    encoded_components = "+".join(components).encode("utf-8")
    return hashlib.sha256(encoded_components).hexdigest()


def __as_absolute_url(root_url: str, url: str) -> str:
    if urlparse(url).netloc:
        return url
    else:
        parsed_root_url = urlparse(root_url)
        return f"{parsed_root_url.scheme}://{parsed_root_url.netloc}/{url}"