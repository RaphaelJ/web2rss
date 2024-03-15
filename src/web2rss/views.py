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


from flask import Response, render_template, redirect, request, url_for

from web2rss.app import app, db
from web2rss.feed import fetch_feed_items, feed_to_rss, create_feed_from_url
from web2rss.forms import URLForm
from web2rss.models import Feed


@app.route("/", methods=["GET", "POST"])
def index():
    form = URLForm(request.form)

    if request.method == "POST" and form.validate():
        feed = create_feed_from_url(form.url.data)

        with db.session.begin():
            db.session.add(feed)
            db.session.commit()

        return redirect(url_for("feed_xml", id=feed.id))
    else:
        return render_template("index.html", form=form)


@app.route("/feed/<int:id>.xml")
def feed_xml(id: int):
    with db.session.begin():
        feed = db.session.query(Feed).get_or_404(id)

    items = fetch_feed_items(feed)

    if items is not None:
        return Response(feed_to_rss(feed, items), mimetype="application/rss+xml")
    else:
        return "Invalid feed", 400
