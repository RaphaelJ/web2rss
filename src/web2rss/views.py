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


from urllib.parse import urlparse

from flask import Response, render_template, redirect, request, url_for

from web2rss.app import app, db
from web2rss.forms import SelectorForm, URLForm
from web2rss.models import Feed
from web2rss.utils.feed import fetch_feed_items, feed_to_rss, create_feed_from_url
from web2rss.utils.proxy import http_proxy


@app.route("/", methods=["GET", "POST"])
def index():
    form = URLForm(request.form)

    if request.method == "POST" and form.validate():
        feed = create_feed_from_url(form.url.data)

        with db.session.begin():
            db.session.add(feed)
            db.session.commit()

        return redirect(url_for("feed_settings", id=feed.id))
    else:
        with db.session.begin():
            feeds = Feed.query.                     \
                order_by(Feed.created_at.desc()).   \
                limit(100).                         \
                all()

        return render_template("index.html", form=form, feeds=feeds)


@app.route("/feed/<int:id>.xml")
def feed_xml(id: int):
    with db.session.begin():
        feed = db.session.query(Feed).get_or_404(id)

    items = fetch_feed_items(feed)

    if items is not None:
        return Response(feed_to_rss(feed, items), mimetype="application/rss+xml")
    else:
        return "Invalid feed. Please update feed settings", 400


@app.route("/feed/<int:id>/settings", methods=["GET", "POST"])
def feed_settings(id: int):
    form = SelectorForm(request.form)

    if request.method == "POST" and form.validate():
        with db.session.begin():
            feed = db.session.query(Feed).get_or_404(id)

            feed.article_selector = form.article_selector.data
            feed.url_selector = form.url_selector.data
            feed.title_selector = form.title_selector.data
            feed.date_selector = form.date_selector.data
            feed.summary_selector = form.summary_selector.data

            db.session.commit()
    else:
        with db.session.begin():
            feed = db.session.query(Feed).get_or_404(id)

    return render_template("feed/settings.html", feed=feed)


@app.route("/feed/<int:id>/proxy/")
@app.route("/feed/<int:id>/proxy/<path:path>")
def feed_proxy(id: int, path: str = ""):
    """Provides an HTTP proxy to the feed's webpage.

    This is required by the feed setting's <iframe> to bypass cross-origin safe guards.
    """

    print(path)

    with db.session.begin():
        feed = db.session.query(Feed).get_or_404(id)

    parsed_url = urlparse(feed.url)

    if path:
        url = f"{parsed_url.scheme}://{parsed_url.hostname}/{path}"
    else:
        url = f"{parsed_url.scheme}://{parsed_url.hostname}"

    proxied_url = lambda proxied_path: url_for("feed_proxy", id=id, path=proxied_path)

    return http_proxy(proxied_url, url, request.args)

