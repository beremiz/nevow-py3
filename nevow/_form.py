"""
Minimal multipart/urlencoded POST body parser.

Replaces the ``cgi.FieldStorage`` usage in ``appserver.py``.  The standard
library ``cgi`` module was removed in Python 3.13 (PEP 594).  This module
provides only the surface that Nevow and Formless rely on:

  - ``FieldStorage`` mapping from field name to either a ``Field`` (single
    occurrence) or a ``list`` of ``Field`` (multiple occurrences with the
    same name).
  - ``Field.name``, ``Field.value``, ``Field.filename``, ``Field.file``.
"""

from io import BytesIO
from email.parser import BytesParser
from email.policy import compat32
from urllib.parse import parse_qsl


class Field:
    def __init__(self, name, value=None, filename=None, file=None):
        self.name = name
        self.value = value
        self.filename = filename
        self.file = file


class FieldStorage:
    def __init__(self):
        self._fields = {}

    def __contains__(self, name):
        return name in self._fields

    def __getitem__(self, name):
        return self._fields[name]

    def __iter__(self):
        return iter(self._fields)

    def keys(self):
        return self._fields.keys()

    def get(self, name, default=None):
        return self._fields.get(name, default)

    def _add(self, field):
        existing = self._fields.get(field.name)
        if existing is None:
            self._fields[field.name] = field
        elif isinstance(existing, list):
            existing.append(field)
        else:
            self._fields[field.name] = [existing, field]


def _get_content_type(headers):
    """Return the raw Content-Type header as bytes, or b'' if absent."""
    if headers is None:
        return b''
    getter = getattr(headers, 'getRawHeaders', None)
    if getter is not None:
        values = getter('content-type')
        if values:
            v = values[0]
            return v.encode('latin-1') if isinstance(v, str) else v
        return b''
    # dict-like fallback (received_headers shim)
    for key in (b'content-type', 'content-type'):
        try:
            v = headers[key]
        except (KeyError, TypeError):
            continue
        return v.encode('latin-1') if isinstance(v, str) else v
    return b''


def parse(content, headers):
    """Parse a POST body and return a populated ``FieldStorage``."""
    fs = FieldStorage()
    content_type = _get_content_type(headers).lower()
    body = content.read()

    if content_type.startswith(b'multipart/form-data'):
        _parse_multipart(fs, body, content_type)
    elif content_type.startswith(b'application/x-www-form-urlencoded') or not content_type:
        _parse_urlencoded(fs, body)
    return fs


def _parse_urlencoded(fs, body):
    if not body:
        return
    text = body.decode('utf-8', errors='replace')
    for name, value in parse_qsl(text, keep_blank_values=True):
        fs._add(Field(name=name, value=value))


def _parse_multipart(fs, body, content_type):
    # Build a synthetic MIME document so email's parser handles the boundary.
    header = b'MIME-Version: 1.0\r\nContent-Type: ' + content_type + b'\r\n\r\n'
    msg = BytesParser(policy=compat32).parsebytes(header + body)
    if not msg.is_multipart():
        return
    for part in msg.get_payload():
        disposition = part.get('content-disposition', '')
        if not disposition:
            continue
        name = part.get_param('name', header='content-disposition')
        if name is None:
            continue
        filename = part.get_param('filename', header='content-disposition')
        payload = part.get_payload(decode=True) or b''
        if filename is not None:
            fs._add(Field(
                name=name,
                value=payload,
                filename=filename,
                file=BytesIO(payload),
            ))
        else:
            try:
                value = payload.decode('utf-8')
            except UnicodeDecodeError:
                value = payload
            fs._add(Field(name=name, value=value))
