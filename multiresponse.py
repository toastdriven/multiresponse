"""
A Python class for Django to provide mime type aware responses. This allows a
client to receive different responses based on the HTTP "Accept" header they
send. This is used in place of ``render_to_response`` or a manual
``HttpResponse``.


Sample Usage:
-------------

  def index(request, extension):
        sample_people = [
            {'name': 'Daniel', 'age': 26},
            {'name': 'John', 'age': 26},
            {'name': 'Jane', 'age': 20},
            {'name': 'Bob', 'age': 35},
        ]

        mr = MultiResponse(request)
        mr.register('html', 'index.html')
        mr.register('xml', 'people.xml')
        mr.register('json', 'people.json')
        mr.register('txt', 'people.txt')
        return mr.render({
            'people': sample_people,
        })
"""
import mimeparse
from django.conf import settings
from django.shortcuts import render_to_response


__version__ = '1.0.1'
__author__ = 'Daniel Lindsley'

ACCEPT_HEADER_MAPPING = {
    'text/html': 'html',
    'application/xml': 'xml',
    'application/json': 'json',
    'text/plain': 'txt',
}


class MultiResponse(object):
    """
    MultiReponse allows you to register different mime types and their templates
    and respond intelligently type to what the client requests.

    Templates must be registered with this class for use in combination with
    the mime type they serve. The mime types may be any of:

        * ``html``
        * ``xml``
        * ``json``
        * ``txt``

    This list can be extended/altered in your settings file by providing a
    ``ACCEPT_HEADER_MAPPING`` mapping with the same structure as the built-in
    mappings (key - actual mime type, value - short mime). By using the short
    mapping, you can serve multiple mime types with the same (appropriate)
    response.
    
    If no appropriate match is found in the "Accept" header, the default mime
    type will be served.
    """
    def __init__(self, request):
        self.request = request
        self.templates = {}
        self.default_type = 'html'
        self.accept_header_mapping = ACCEPT_HEADER_MAPPING
        
        if hasattr(settings, 'ACCEPT_HEADER_MAPPING'):
            self.accept_header_mapping.update(settings.ACCEPT_HEADER_MAPPING)
    
    def register(self, mime_type, template, default=False):
        """
        Registers a mime type and corresponding template.
        
        By default, the first type registered becomes the default. You can
        override this by passing the third argument ``default`` as ``True`` on
        a later call as desired.
        """
        if self.templates == {} or default is True:
            self.default_type = mime_type
        
        self.templates[mime_type] = template
    
    def render(self, context=None, **kwargs):
        """
        Renders the desired template (determined via the client's accepted mime
        types) with the context. Accepts the same kwargs as render_to_response. 
        """
        desired_template = ''
        content_type = 'text/html'
        
        if self.templates == {}:
            raise RuntimeError('You must register at least one mime type and template with MultiResponse before rendering.')
        
        if 'HTTP_ACCEPT' in self.request.META:
            registered_types = []
            
            for mime, short in self.accept_header_mapping.items():
                if short in self.templates.keys():
                    registered_types.append(mime)
            
            content_type = mimeparse.best_match(registered_types, self.request.META['HTTP_ACCEPT'])
            short_type = self.accept_header_mapping.get(content_type)
            
            if short_type in self.templates.keys():
                desired_template = self.templates.get(short_type)
    
        if not desired_template:
            try:
                desired_template = self.templates.get(self.default_type)
                # Fail miserably.
                content_type = 'text/plain'
            except KeyError:
                raise RuntimeError('The default mime type could not be found in the registered templates.')
    
        response = render_to_response(desired_template, context, **kwargs)
        response['Content-Type'] = "%s; charset=%s" % (content_type, settings.DEFAULT_CHARSET)
        return response
