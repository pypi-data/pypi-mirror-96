import os
import re
import string
from tornado.web import HTTPError

from .web.base import _f


class InvalidFormat(HTTPError):
    """User-supplied value doesn't pass validation."""
    def __init__(self, message, status_code=400):
        HTTPError.__init__(self, status_code, message)
        self.message = message

    def __repr__(self):
        return "InvalidFormat(%r, %d)" % (self.message, self.status_code)


def project_name(name):
    if not name:
        raise InvalidFormat(_f("Project name cannot be empty"))
    if len(name) > 50:
        raise InvalidFormat(_f("Project name is too long"))


def project_description(description):
    if len(description) > 102400:
        raise InvalidFormat(_f("Project description is too long"))


ALLOWED_LOGIN_CHARACTERS_NEW = (
    string.ascii_lowercase + string.digits +
    '._-'
)
ALLOWED_LOGIN_CHARACTERS = (
    ALLOWED_LOGIN_CHARACTERS_NEW + '+@ '
)


def user_login(login, new=False):
    if not login:
        raise InvalidFormat(_f("User login cannot be empty"))
    if len(login) > (20 if new else 25):
        raise InvalidFormat(_f("User login is too long"))
    login = login.lower()
    chars = ALLOWED_LOGIN_CHARACTERS_NEW if new else ALLOWED_LOGIN_CHARACTERS
    if any(c not in chars for c in login):
        raise InvalidFormat(_f("User login contains forbidden characters"))
    return login


def user_email(email):
    if not email:
        raise InvalidFormat(_f("Email cannot be empty"))  # but it can be NULL
    if '@' not in email:
        raise InvalidFormat(_f("Invalid email address"))


def user_password(password):
    if len(password) < 5:
        raise InvalidFormat(_f("Please use a longer password"))
    if len(password) > 5120:
        raise InvalidFormat(_f("Please use a shorter password"))


def document_name(name):
    if not name:
        raise InvalidFormat(_f("Document name cannot be empty"))
    if len(name) > 50:
        raise InvalidFormat(_f("Document name is too long"))


def document_description(description):
    if len(description) > 102400:
        raise InvalidFormat(_f("Document description is too long"))


def tag_path(path):
    if not path:
        raise InvalidFormat(_f("Tag path cannot be empty"))
    if len(path) > 200:
        raise InvalidFormat(_f("Tag path is too long"))


def tag_description(description):
    if len(description) > 102400:
        raise InvalidFormat(_f("Tag description is too long"))


_windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1',
                         'LPT2', 'LPT3', 'PRN', 'NUL')
_not_ascii_re = re.compile(r'[^A-Za-z0-9_.-]')


def filename(name):
    """Sanitize a filename.

    This takes a filename, for example provided by a browser with a file
    upload, and turn it into something that is safe for opening.

    Adapted from werkzeug's secure_filename(), copyright 2007 the Pallets team.
    https://palletsprojects.com/p/werkzeug/
    """
    if '/' in name:
        name = name[name.rindex('/') + 1:]
    if filename.windows and '\\' in name:
        # It seems that IE gets that wrong, at least when the file is from
        # a network share
        name = name[name.rindex('\\') + 1:]
    name, ext = os.path.splitext(name)
    name = name[:20]
    name = _not_ascii_re.sub('', name).strip('._')
    if not name:
        name = '_'
    ext = _not_ascii_re.sub('', ext)
    if (
        filename.windows
        and name.split('.')[0].upper() in _windows_device_files
    ):
        name = '_' + name
    name = name + ext
    return name


filename.windows = os.name == 'nt'
