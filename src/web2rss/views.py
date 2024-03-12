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


from flask import Response, render_template

from web2rss.app import app, db
from web2rss.feed import fetch_feed_items, feed_to_rss
from web2rss.models import Feed


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/feed/<int:id>.xml")
def feed(id: int):
    with db.session.begin():
        feed = db.session.query(Feed).get_or_404(id)

    items = fetch_feed_items(feed)

    if items is not None:
        return Response(feed_to_rss(feed, items), mimetype="application/rss+xml")
    else:
        return "Invalid feed", 400
