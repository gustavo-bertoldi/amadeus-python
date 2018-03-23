# Support Ruby 2 and 3 API calls without importing
# a 3rd party library
try:
    from urllib.request import Request as HTTPRequest
    from urllib.parse import urlencode
except ImportError:
    from urllib2 import Request as HTTPRequest
    from urllib import urlencode


class Request(object):
    def __init__(self, options):
        self._initialize_options(options)
        self._initialize_headers()
        self._build_http_request()

    # PRIVATE

    # Initializes the Request object with all the passed in params. These
    # do not change once set
    def _initialize_options(self, options):
        self.host = options['host']
        self.port = options['port']
        self.ssl = options['ssl']
        self.scheme = 'https' if self.ssl else 'http'
        self.verb = options['verb']
        self.path = options['path']
        self.params = options['params']
        self.bearer_token = options['bearer_token']
        self.client_version = options['client_version']
        self.language_version = options['language_version']
        self.app_id = options['app_id']
        self.app_version = options['app_version']

    # Initializes the basic headers
    def _initialize_headers(self):
        self.headers = {
            'User-Agent': self.build_user_agent(),
            'Accept': 'application/json'
        }

    # Determines the User Agent
    def build_user_agent(self):
        user_agent = "amadeus-python/{0}".format(self.client_version)
        user_agent += " python/{0}".format(self.language_version)
        if self.app_id:
            user_agent += " {0}/{1}".format(self.app_id, self.app_version)
        return user_agent

    # Builds up a HTTP Request objectm if not akready set
    def _build_http_request(self):
        if (not hasattr(self, 'http_request')):
            request = self._request_for_verb()
            self._add_post_data_header()
            self._add_bearer_token_header()
            self._apply_headers(request)
            self.http_request = request

    # Builds a HTTP Request object based on the path, params, and verb
    def _request_for_verb(self):
        params = self._encoded_params().encode()
        path = self._full_url()

        if (self.verb == 'GET'):
            return HTTPRequest(path)
        else:
            return HTTPRequest(path, params)

    # Encodes the params before sending them
    def _encoded_params(self):
        return urlencode(self.params)

    # Builds up the full URL based on the scheme, host, path, and params
    def _full_url(self):
        full_url = "{0}://{1}{2}".format(self.scheme, self.host, self.path)
        if (self.verb == 'GET'):
            full_url += "?{0}".format(self._encoded_params())
        return full_url

    # Adds an extra header if the verb is POST
    def _add_post_data_header(self):
        if (self.verb == 'POST'):
            self.headers['Content-Type'] = 'application/x-www-form-urlencoded'

    # Adds the authentication header if the bearer token has been set
    def _add_bearer_token_header(self):
        if (self.bearer_token is not None):
            self.headers['Authorization'] = self.bearer_token

    # Applies all the headers to the HTTP Request object
    def _apply_headers(self, http_request):
        for key in self.headers:
            http_request.add_header(key, self.headers[key])
