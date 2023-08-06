import argparse
import asyncio
import base64
import gettext
import locale
import logging
import os
import pkg_resources
import prometheus_client
import re
import subprocess
import sys
import tornado.ioloop
from urllib.parse import urlparse
import webbrowser

import taguette
from . import __version__
from .database import migrate
from .web import make_app


logger = logging.getLogger(__name__)

PROM_VERSION = prometheus_client.Gauge('version', "Application version",
                                       ['version'])


def prepare_db(database):
    # Windows paths kinda look like URLs, but aren't
    if sys.platform == 'win32' and re.match(r'^[a-zA-Z]:\\', database):
        logger.info("Database URL recognized as Windows path")
        url = None
    else:
        url = urlparse(database)
    if url is not None and url.scheme:
        # Full URL: use it, create path if sqlite
        db_url = database
        if url.scheme == 'sqlite' and url.path.startswith('/'):
            os.makedirs(url.path[1:])
    else:
        # Path: create it, turn into URL
        database = os.path.expanduser(database)
        if os.path.dirname(database):
            os.makedirs(os.path.dirname(database), exist_ok=True)
        db_url = 'sqlite:///' + database
        logger.info("Turning database path into URL: %s", db_url)
    return db_url


def default_config(output):
    if output is None:
        out = sys.stdout
    else:
        out = open(output, 'w')
    out.write('''\
# This is the configuration file for Taguette
# It is a Python file, so you can use the full Python syntax

# Name of this server
NAME = "Misconfigured Taguette Server"

# Address and port to listen on
BIND_ADDRESS = "0.0.0.0"
PORT = 7465

# A unique secret key that will be used to sign cookies
SECRET_KEY = "{secret}"

# Database to use
# This is a SQLAlchemy connection URL; refer to their documentation for info
# https://docs.sqlalchemy.org/en/latest/core/engines.html
# If using SQLite3 on Unix, note the 4 slashes for an absolute path
# (keep 3 before a relative path)
DATABASE = "sqlite:////non/existent/taguette/database.sqlite3"

# Address to send system emails from
EMAIL = "Misconfigured Taguette Server <taguette@example.com>"

# Default language
DEFAULT_LANGUAGE = 'en_US'

# SMTP server to use to send emails
MAIL_SERVER = {{
    "ssl": False,
    "host": "localhost",
    "port": 25,
}}

# Whether users must explicitly accept cookies before using the website
COOKIES_PROMPT = False

# Whether new users can create an account
REGISTRATION_ENABLED = True

# Set this to true if you are behind a reverse proxy that sets the
# X-Forwarded-For header.
# Leave this at False if users are connecting to Taguette directly
X_HEADERS = False

# Time limits for converting documents
CONVERT_TO_HTML_TIMEOUT = 3 * 60  # 3min for importing document into Taguette
CONVERT_FROM_HTML_TIMEOUT = 3 * 60  # 3min for exporting from Taguette

# If you want to export metrics using Prometheus, set a port number here
#PROMETHEUS_LISTEN = "0.0.0.0:9101"

# If you want to report errors to Sentry, set your DSN here
#SENTRY_DSN = "https://<key>@sentry.io/<project>"
'''.format(secret=base64.b64encode(os.urandom(30)).decode('ascii')))
    if output is not None:
        out.close()


DEFAULT_CONFIG = {
    'MULTIUSER': True,
    'BIND_ADDRESS': '0.0.0.0',
    'REGISTRATION_ENABLED': True,
    'DEFAULT_LANGUAGE': 'en_US',
    'CONVERT_FROM_HTML_TIMEOUT': 3 * 60,
    'CONVERT_TO_HTML_TIMEOUT': 3 * 60,
    'OPF_OUT_SIZE_LIMIT': 5000000,  # 5 MB
    'HTML_OUT_SIZE_LIMIT': 2000000,  # 2 MB
}

REQUIRED_CONFIG = ['NAME', 'PORT', 'SECRET_KEY', 'DATABASE', 'X_HEADERS',
                   'EMAIL', 'MAIL_SERVER', 'COOKIES_PROMPT',
                   'OPF_OUT_SIZE_LIMIT', 'HTML_OUT_SIZE_LIMIT']


def main():
    logging.root.handlers.clear()
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s: %(message)s")
    locale.setlocale(locale.LC_ALL, '')
    lang = locale.getlocale()[0]
    lang = [lang] if lang else []
    d = pkg_resources.resource_filename('taguette', 'l10n')
    trans = gettext.translation('taguette_main', d, lang, fallback=True)
    taguette._trans = trans
    _ = trans.gettext

    if sys.platform == 'win32' and sys.version_info >= (3, 8):
        # https://github.com/tornadoweb/tornado/issues/2608
        try:
            from asyncio import WindowsSelectorEventLoopPolicy
        except ImportError:
            pass
        else:
            policy = asyncio.get_event_loop_policy()
            if not isinstance(policy, WindowsSelectorEventLoopPolicy):
                asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    if sys.platform == 'win32':
        import ctypes.wintypes

        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value

        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None,
                                               SHGFP_TYPE_CURRENT, buf)

        default_db = os.path.join(buf.value, 'Taguette', 'taguette.sqlite3')
        default_db_show = os.path.join(os.path.basename(buf.value),
                                       'Taguette', 'taguette.sqlite3')
    else:
        data = os.environ.get('XDG_DATA_HOME')
        if not data:
            data = os.path.join(os.environ['HOME'], '.local', 'share')
            default_db_show = '$HOME/.local/share/taguette/taguette.sqlite3'
        else:
            default_db_show = '$XDG_DATA_HOME/taguette/taguette.sqlite3'
        default_db = os.path.join(data, 'taguette', 'taguette.sqlite3')

    parser = argparse.ArgumentParser(
        description="Document tagger for qualitative analysis",
    )
    parser.add_argument('--version', action='version',
                        version='taguette version %s' % __version__)
    parser.add_argument('-p', '--port', default='7465',
                        help=_("Port number on which to listen"))
    parser.add_argument('-b', '--bind', default='127.0.0.1',
                        help=_("Address to bind on"))
    parser.add_argument('--browser', action='store_true', default=True,
                        help=_("Open web browser to the application"))
    parser.add_argument('--no-browser', action='store_false', dest='browser',
                        help=_("Don't open the web browser"))
    parser.add_argument('--debug', action='store_true', default=False,
                        help=argparse.SUPPRESS)
    parser.add_argument('--database', action='store',
                        default=default_db,
                        help=_("Database location or connection string, for "
                               "example 'project.db' or "
                               "'postgresql://me:pw@localhost/mydb' "
                               "(default: %(default)r)") %
                        dict(default=default_db_show))
    parser.add_argument('--set-umask', action='store', dest='umask',
                        default="077",
                        help=_("Set the file creation mask (umask) on systems "
                               "that support it."))
    parser.add_argument('--dont-set-umask', action='store_const', dest='umask',
                        const=None,
                        help=_("Don't change umask on startup"))
    parser.set_defaults(func=None)

    subparsers = parser.add_subparsers(title=_("additional commands"),
                                       metavar='', dest='cmd')

    parser_migrate = subparsers.add_parser('migrate',
                                           help=_("Manually trigger a "
                                                  "database migration"))
    parser_migrate.add_argument('revision', action='store', default='head',
                                nargs=argparse.OPTIONAL)
    parser_migrate.set_defaults(
        func=lambda args: migrate(prepare_db(args.database), args.revision))

    parser_config = subparsers.add_parser(
        'default-config',
        help=_("Print the default server configuration"))
    parser_config.add_argument('--output', '-o', action='store', nargs=1,
                               help=_("Output to this file rather than "
                                      "stdout"))
    parser_config.set_defaults(func=lambda args: default_config(args.output))

    parser_server = subparsers.add_parser(
        'server',
        help=_("Run in server mode, suitable for a multi-user deployment"))
    parser_server.add_argument('config_file',
                               help=_("Configuration file for the server. The "
                                      "default configuration can be generated "
                                      "using the `default-config` command"))

    args = parser.parse_args()

    if args.umask is not None:
        if not re.match(r'^[0-7][0-7][0-7]$', args.umask):
            print(_("Invalid umask: %(arg)s") % dict(arg=args.umask),
                  file=sys.stderr, flush=True)
            sys.exit(2)
        logger.info("Setting umask to %s", args.umask)
        os.umask(int(args.umask, 8))

    if args.func:
        args.func(args)
        sys.exit(0)

    if args.cmd == 'server':
        # Set configuration from config file
        config = {}
        with open(args.config_file) as fp:
            exec(fp.read(), config)
        config = dict(
            DEFAULT_CONFIG,
            **config
        )
        missing = False
        for key in REQUIRED_CONFIG:
            if key not in config:
                print(_("Missing required configuration variable %(var)s") %
                      dict(var=key),
                      file=sys.stderr, flush=True)
                missing = True
        if missing:
            sys.exit(2)
    else:
        if args.debug:
            # Use a deterministic secret key, to avoid it changing during
            # auto-reload and such
            secret = 'debug'
        else:
            secret = os.urandom(30).decode('iso-8859-15')

        # Set configuration from command-line
        config = dict(
            DEFAULT_CONFIG,
            MULTIUSER=False,
            BIND_ADDRESS=args.bind,
            X_HEADERS=False,
            PORT=int(args.port),
            DATABASE=prepare_db(args.database),
            SECRET_KEY=secret,
            COOKIES_PROMPT=False,
            HTML_OUT_SIZE_LIMIT=5000000,  # 5 MB
        )

    if 'PROMETHEUS_LISTEN' in config:
        p_addr = None
        p_port = config['PROMETHEUS_LISTEN']
        if isinstance(p_port, str):
            if ':' in p_port:
                p_addr, p_port = p_port.split(':')
                p_addr = p_addr or None
            p_port = int(p_port)
        logger.info("Starting Prometheus exporter on port %d", p_port)
        prometheus_client.start_http_server(p_port, p_addr)

    try:
        version = subprocess.check_output(
            ['git', '--git-dir=.git', 'describe'],
            cwd=os.path.dirname(os.path.dirname(__file__)),
            stderr=subprocess.PIPE,
        ).decode('utf-8').strip()
    except (OSError, subprocess.CalledProcessError):
        version = 'v%s' % __version__
        logger.info("Not a Git repository, using version=%s", version)
    else:
        logger.info("Running from Git repository, using version=%s",
                    version)
    PROM_VERSION.labels(version).set(1)

    if 'SENTRY_DSN' in config:
        import sentry_sdk
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        from sentry_sdk.integrations.tornado import TornadoIntegration
        logger.info("Initializing Sentry")
        sentry_sdk.init(
            dsn=config['SENTRY_DSN'],
            integrations=[TornadoIntegration(), SqlalchemyIntegration()],
            ignore_errors=[KeyboardInterrupt],
            release='taguette@%s' % version,
        )

    app = make_app(config, debug=args.debug)
    app.listen(config['PORT'], address=config['BIND_ADDRESS'],
               xheaders=config.get('X_HEADERS', False))
    loop = tornado.ioloop.IOLoop.current()

    token = app.single_user_token
    if token:
        url = 'http://localhost:%d/?token=%s' % (config['PORT'], token)
    else:
        url = 'http://localhost:%d/' % config['PORT']
    print(_("\n    Taguette %(version)s is now running. You can connect to it "
            "using this link:\n\n    %(url)s\n") %
          dict(url=url, version=__version__), flush=True)

    if args.browser and not args.debug:
        loop.call_later(0.01, webbrowser.open, url)

    loop.start()


if __name__ == '__main__':
    main()
