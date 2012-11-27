import hmac, base64, binascii, re
from tg.support.objectproxy import TurboGearsObjectProxy
from tg.support.registry import StackedObjectProxy, DispatchingConfig
from tg.caching import cached_property

try:
    import cPickle as pickle
except ImportError: #pragma: no cover
    import pickle

try:
    from hashlib import sha1
except ImportError: #pragma: no cover
    import sha as sha1

from webob import Request as WebObRequest
from webob import Response as WebObResponse

class Request(WebObRequest):
    """WebOb Request subclass

    The WebOb :class:`webob.Request` has no charset, or other defaults. This subclass
    adds defaults, along with several methods for backwards
    compatibility with paste.wsgiwrappers.WSGIRequest.

    """
    def languages_best_match(self, fallback=None):
        al = self.accept_language
        try:
            items = [i for i, q in sorted(al._parsed, key=lambda iq: -iq[1])]
        except AttributeError:
            #NilAccept has no _parsed, here for test units
            items = []

        if fallback:
            for index, item in enumerate(items):
                if al._match(item, fallback):
                    items[index:] = [fallback]
                    break
            else:
                items.append(fallback)

        return items

    @property
    def controller_state(self):
        return self._controller_state

    @property
    def fast_path(self):
        return self.path

    @cached_property
    def plain_languages(self):
        return self.languages_best_match()

    @property
    def languages(self):
        return self.languages_best_match(self._language)

    @property
    def language(self):
        return self._language

    @language.setter
    def language(self, value):
        self._language = value

    @property
    def response_type(self):
        return self._response_type

    def match_accept(self, mimetypes):
        return self.accept.first_match(mimetypes)

    def signed_cookie(self, name, secret):
        """Extract a signed cookie of ``name`` from the request

        The cookie is expected to have been created with
        ``Response.signed_cookie``, and the ``secret`` should be the
        same as the one used to sign it.

        Any failure in the signature of the data will result in None
        being returned.

        """
        cookie = self.str_cookies.get(name)
        if not cookie:
            return
        try:
            sig, pickled = cookie[:40], base64.decodestring(cookie[40:])
        except binascii.Error:
            # Badly formed data can make base64 die
            return
        if hmac.new(secret, pickled, sha1).hexdigest() == sig:
            return pickle.loads(pickled)

    @property
    def str_cookies(self):
        return self.cookies

    @cached_property
    def args_params(self):
        return dict(((str(n), v) for n,v in self.params.mixed().items()))

    def _fast_setattr(self, name, value):
        object.__setattr__(self, name, value)

class Response(WebObResponse):
    """WebOb Response subclass

    The WebOb Response has no default content type, or error defaults.
    This subclass adds defaults, along with several methods for
    backwards compatibility with paste.wsgiwrappers.WSGIResponse.

    """
    content = WebObResponse.body

    def determine_charset(self):
        return self.charset

    def has_header(self, header):
        return header in self.headers

    def get_content(self):
        return self.body

    def write(self, content):
        self.body_file.write(content)

    def wsgi_response(self):
        return self.status, self.headers, self.body

    def signed_cookie(self, name, data, secret=None, **kwargs):
        """Save a signed cookie with ``secret`` signature

        Saves a signed cookie of the pickled data. All other keyword
        arguments that ``WebOb.set_cookie`` accepts are usable and
        passed to the WebOb set_cookie method after creating the signed
        cookie value.

        """
        pickled = pickle.dumps(data, pickle.HIGHEST_PROTOCOL)
        sig = hmac.new(secret, pickled, sha1).hexdigest()
        self.set_cookie(name, sig + base64.encodestring(pickled), **kwargs)

config = DispatchingConfig()
context = StackedObjectProxy(name="context")

class TurboGearsContextMember(TurboGearsObjectProxy):
    """Member of the TurboGears request context.

    Provides access to turbogears context members
    like request, response, template context and so on

    """

    def __init__(self, name):
        self.__dict__['name'] = name

    def _current_obj(self):
        return getattr(context, self.name)


request = TurboGearsContextMember(name="request")
app_globals = TurboGearsContextMember(name="app_globals")
cache = TurboGearsContextMember(name="cache")
response = TurboGearsContextMember(name="response")
session = TurboGearsContextMember(name="session")
tmpl_context = TurboGearsContextMember(name="tmpl_context")
url = TurboGearsContextMember(name="url")
translator = TurboGearsContextMember(name="translator")

__all__ = ['app_globals', 'request', 'response', 'tmpl_context', 'session', 'cache', 'translator', 'url', 'config']