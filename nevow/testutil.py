# -*- test-case-name: nevow.test.test_testutil -*-
# Copyright (c) 2004-2010 Divmod.
# See LICENSE for details.

import os, sys

from zope.interface import implementer

from twisted.python.components import Componentized
from twisted.trial.unittest import TestCase as TrialTestCase
from twisted.internet import defer
from twisted.web import http

from formless import iformless

from nevow import inevow, context, appserver
from nevow.util import unicode, toBytes

class FakeChannel:
    def __init__(self, site):
        self.site = site


class FakeSite:
    pass

@implementer(inevow.ISession)
class FakeSession(Componentized):
    def __init__(self, avatar):
        Componentized.__init__(self)
        self.avatar = avatar
        self.uid = 12345
    def getLoggedInRoot(self):
        return self.avatar


fs = FakeSession(None)

@implementer(inevow.IRequest)
class FakeRequest(Componentized):
    """
    Implementation of L{inevow.IRequest} which is convenient to use in unit
    tests.

    @ivar lastModified: The value passed to L{setLastModified} or C{None} if
        that method has not been called.

    @type accumulator: C{str}
    @ivar accumulator: The bytes written to the response body.

    @type deferred: L{Deferred}
    @ivar deferred: The deferred which represents rendering of the response
        to this request.  This is basically an implementation detail of
        L{NevowRequest}.  Application code should probably never use this.

    @ivar _appRootURL: C{None} or the object passed to L{rememberRootURL}.
    """

    fields = None
    failure = None
    context = None
    redirected_to = None
    lastModified = None
    content = ""
    method = 'GET'
    code = http.OK
    deferred = None
    accumulator = ''
    _appRootURL = None

    def __init__(self, headers=None, args=None, avatar=None,
                 uri='/', currentSegments=None, cookies=None,
                 user="", password="", isSecure=False):
        """
        Create a FakeRequest instance.

        @param headers: dict of request headers
        @param args: dict of args
        @param avatar: avatar to pass to the FakeSession instance
        @param uri: request URI
        @param currentSegments: list of segments that have "already been located"
        @param cookies: dict of cookies
        @param user: username (like in http auth)
        @param password: password (like in http auth)
        @param isSecure: whether this request represents an HTTPS url
        """
        Componentized.__init__(self)
        self.uri = uri
        if not uri.startswith('/'):
            raise ValueError('uri must be relative with absolute path')
        self.path = uri
        self.prepath = []
        postpath = uri.split('?')[0]
        assert postpath.startswith('/')
        self.postpath = postpath[1:].split('/')
        if currentSegments is not None:
            for seg in currentSegments:
                assert seg == self.postpath[0]
                self.prepath.append(self.postpath.pop(0))
        else:
            self.prepath.append('')
        self.headers = {}
        self.args = args or {}
        self.sess = FakeSession(avatar)
        self.site = FakeSite()
        self.received_headers = {}
        if headers:
            for k, v in headers.items():
                self.received_headers[k.lower()] = v
        if cookies is not None:
            self.cookies = cookies
        else:
            self.cookies = {}
        self.user = user
        self.password = password
        self.secure = isSecure
        self.deferred = defer.Deferred()

    def URLPath(self):
        from nevow import url
        return url.URL.fromString('')

    def getSession(self):
        return self.sess

    def registerProducer(self, producer, streaming):
        """
        Synchronously cause the given producer to produce all of its data.

        This will not work with push producers.  Do not use it with them.
        """
        keepGoing = [None]
        self.unregisterProducer = keepGoing.pop
        while keepGoing:
            producer.resumeProducing()
        del self.unregisterProducer

    def v():
        def get(self):
            return self.accumulator
        return get,
    v = property(*v())

    def write(self, bytes):
        """
        Accumulate the given bytes as part of the response body.

        @type bytes: C{str}
        """
        self.accumulator += bytes


    finished = False
    def finishRequest(self, success):
        self.finished = True

    def finish(self):
        self.deferred.callback('')

    def getHeader(self, key):
        return self.received_headers.get(key.lower())

    def setHeader(self, key, val):
        self.headers[key.lower()] = val

    def redirect(self, url):
        self.redirected_to = url

    def processingFailed(self, f):
        self.failure = f

    def setResponseCode(self, code):
        self.code = code

    def setLastModified(self, when):
        self.lastModified = when

    def prePathURL(self):
        """
        The absolute URL up until the last handled segment of this request.

        @rtype: C{str}.
        """
        return 'http://%s/%s' % (unicode(self.getHeader('host')) or 'localhost',
                                 unicode(b'/'.join(self.prepath)))

    def getClientIP(self):
        return '127.0.0.1'

    def addCookie(self, k, v, expires=None, domain=None, path=None, max_age=None, comment=None, secure=None):
        """
        Set a cookie for use in subsequent requests.
        """
        self.cookies[k] = v

    def getCookie(self, k):
        """
        Fetch a cookie previously set.
        """
        return self.cookies.get(k)

    def getUser(self):
        """
        Returns the HTTP auth username.
        """
        return self.user

    def getPassword(self):
        """
        Returns the HTTP auth password.
        """
        return self.password

    def getRootURL(self):
        """
        Return the previously remembered URL.
        """
        return self._appRootURL


    def rememberRootURL(self, url=None):
        """
        For compatibility with appserver.NevowRequest.
        """
        if url is None:
            raise NotImplementedError(
                "Default URL remembering logic is not implemented.")
        self._appRootURL = url


    def isSecure(self):
        """
        Returns whether this is an HTTPS request or not.
        """
        return self.secure


class TestCase(TrialTestCase):
    hasBools = (sys.version_info >= (2,3))
    _assertions = 0

    # This should be migrated to Twisted.
    def failUnlessSubstring(self, containee, container, msg=None):
        self._assertions += 1
        if container.find(containee) == -1:
            self.fail(msg or "%r not in %r" % (containee, container))
    def failIfSubstring(self, containee, container, msg=None):
        self._assertions += 1
        if container.find(containee) != -1:
            self.fail(msg or "%r in %r" % (containee, container))

    assertSubstring = failUnlessSubstring
    assertNotSubstring = failIfSubstring

    def assertNotIdentical(self, first, second, msg=None):
        self._assertions += 1
        if first is second:
            self.fail(msg or '%r is %r' % (first, second))

    def failIfIn(self, containee, container, msg=None):
        self._assertions += 1
        if containee in container:
            self.fail(msg or "%r in %r" % (containee, container))

    def assertApproximates(self, first, second, tolerance, msg=None):
        self._assertions += 1
        if abs(first - second) > tolerance:
            self.fail(msg or "%s ~== %s" % (first, second))


if not hasattr(TrialTestCase, 'mktemp'):
    def mktemp(self):
        import tempfile
        return tempfile.mktemp()
    TestCase.mktemp = mktemp

@implementer(iformless.IFormDefaults)
class AccumulatingFakeRequest(FakeRequest):
    """
    I am a fake IRequest that is also a stub implementation of
    IFormDefaults.

    This class is named I{accumulating} for historical reasons only.  You
    probably want to ignore this and use L{FakeRequest} instead.
    """

    def __init__(self, *a, **kw):
        FakeRequest.__init__(self, *a, **kw)
        self.d = defer.Deferred()

    def getDefault(self, key, context):
        return ''

    def remember(self, object, interface):
        pass


def renderPage(res, topLevelContext=context.WebContext,
               reqFactory=FakeRequest):
    """
    Render the given resource.  Return a Deferred which fires when it has
    rendered.
    """
    req = reqFactory()
    ctx = topLevelContext(tag=res)
    ctx.remember(req, inevow.IRequest)

    render = appserver.NevowRequest(None, True).gotPageContext

    result = render(ctx)
    result.addCallback(lambda x: req.accumulator)
    return result
