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


import requests
from requests import RequestException

from wtforms import Form, StringField, URLField
from wtforms.validators import DataRequired, Optional, ValidationError


class URLForm(Form):
    url = URLField("Webpage URL", validators=[DataRequired()])

    def validate_url(self, field):
        try:
            response = requests.get(field.data)
            if not (200 <= response.status_code < 300):
                raise ValidationError("The website returned an invalid response.")
        except RequestException as _e:
            raise ValidationError("An error occured when trying to reach the website.")


class SelectorForm(Form):
    article = StringField("Article", validators=[Optional()], filters=[lambda x: x or None])

    link = StringField("Link", validators=[Optional()], filters=[lambda x: x or None])
    title = StringField("Title", validators=[Optional()], filters=[lambda x: x or None])
    date = StringField("Publication date", validators=[Optional()], filters=[lambda x: x or None])
    author = StringField("Author", validators=[Optional()], filters=[lambda x: x or None])
    summary = StringField("Summary", validators=[Optional()], filters=[lambda x: x or None])
