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


import os.path

from typing import Callable, Optional, Mapping

import bs4
import requests

from flask import Response


def http_proxy(proxied_url: Callable[[str], str], url: str, params: Mapping[str, str]) -> Response:
    print("Proxied URL:", url)

    resp = requests.get(url, params=params, allow_redirects=False)

    headers = _proxied_headers(proxied_url, resp.headers)

    content_type = resp.headers.get("content-type")

    if content_type is not None and content_type.startswith("text/html"):
        content = _proxied_html(proxied_url, resp.text)
    else:
        content = resp.content

    return Response(content, resp.status_code, headers, content_type=content_type)


def _proxied_headers(proxied_url: Callable[[str], str], headers: Mapping[str, str]):
    if "location" in headers:
        headers["location"] = proxied_url(headers["location"][:1])

    for excluded in ["content-encoding", "content-length", "transfer-encoding", "connection"]:
        if excluded in headers:
            del headers[excluded]


def _proxied_html(proxied_url: Callable[[str], str], html: str) -> str:
    """Transforms absolute URLs to their proxied equivalents in an HTML page."""

    dom = bs4.BeautifulSoup(html, "html.parser")

    for link in dom.select("[href^='/']"):
        link["href"] = proxied_url(link["href"][1:])

    for media in dom.select("[src^='/']"):
        media["src"] = proxied_url(media["src"][1:])

    return str(dom)
