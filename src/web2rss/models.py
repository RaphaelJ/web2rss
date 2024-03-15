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


from datetime import datetime, timezone

from web2rss.app import db


class Feed(db.Model):
    __tablename__ = 'feed'

    id = db.Column(db.Integer, primary_key=True)

    created_at = db.Column(
        db.DateTime(), nullable=False, default=lambda: datetime.now(tz=timezone.utc)
    )

    url = db.Column(db.String(), nullable=False)
    page_title = db.Column(db.String(), nullable=False)

    article_selector = db.Column(db.String(), nullable=True)
    url_selector = db.Column(db.String(), nullable=True)
    title_selector = db.Column(db.String(), nullable=True)
    date_selector = db.Column(db.String(), nullable=True)
    summary_selector = db.Column(db.String(), nullable=True)
