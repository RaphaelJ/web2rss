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


import argparse
import code
import logging

from web2rss.app import app, db


logger = logging.getLogger(__name__)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(name)s:%(lineno)d %(message)s",
    )

    parser = argparse.ArgumentParser("web2rss", description="Parses webpages as RSS feeds.")

    subparsers = parser.add_subparsers(required=True)

    run = subparsers.add_parser("run", description="runs the webapp.")
    run.add_argument("--host", type=str, default=None)
    run.add_argument("--port", type=int, default=None)
    run.set_defaults(handler=_run)

    create_tables = subparsers.add_parser(
        "create_tables",
        description="creates the required database tables."
    )
    create_tables.set_defaults(handler=_create_tables)

    shell = subparsers.add_parser(
        "shell",
        description="opens a Python shell with the application object."
    )
    shell.set_defaults(handler=_shell)

    args = parser.parse_args()
    args.handler(args)


def _run(args: argparse.Namespace):
    app.run(args.host, args.port)


def _create_tables(_args: argparse.Namespace):
    with app.app_context():
        db.create_all()


def _shell(args: argparse.Namespace):
    with app.app_context():
        with db.session.begin():
            code.interact()


if __name__ == "__main__":
    main()
