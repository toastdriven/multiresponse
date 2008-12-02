from django.conf import settings
from django.shortcuts import render_to_response


ACCEPT_HEADER_MAPPING = {
    'text/html': 'html',
    'application/xml': 'xml',
    'text/xml': 'xml', # Broken but we're including it.
    'application/json': 'json',
    'text/plain': 'text',
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
    
    def client_accepted_mime_types(self):
        accepted_mime_types = []
        
        for mime in self.request.META.get('HTTP_ACCEPT').split(','):
            mime_no_whitespace = mime.strip()
            mime_info = mime_no_whitespace.split(';')
            # We don't handle levels/qualities right now, though we should eventually.
            cleaned_mime = mime_info[0]
            accepted_mime_types.append(cleaned_mime)
        
        return accepted_mime_types
    
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
    
    def determine_extension(self):
        """Attempt to intelligently discern from the URL what the desired 
        extension is."""
        desired_extension = None
        request_path_pieces = [piece for piece in self.request.path.split('/') if piece != '']
        
        try:
            # Just look at the last bit.
            extension = request_path_pieces.pop()
            
            if extension in self.templates.keys():
                desired_extension = extension
        except IndexError:
            # Fail silently.
            pass
        
        return desired_extension
    
    def render(self, context=None, **kwargs):
        """Renders the desired template with the context. Accepts the same
        kwargs as render_to_response."""
        desired_template = ''
        content_type = 'text/html'
        
        if self.templates == {}:
            raise RuntimeError('You must register at least one mime type and template with MultiResponse before rendering.')
        
        if 'HTTP_ACCEPT' in self.request.META:
            extension = self.determine_extension()
            
            if extension in self.templates.keys():
                for mime in self.client_accepted_mime_types():
                    if mime in self.accept_header_mapping and self.accept_header_mapping[mime] == extension:
                        content_type = mime
                        desired_template = self.templates[extension]
                        break
    
        if not desired_template:
            try:
                desired_template = self.templates.get(self.default_type)
            except KeyError:
                raise RuntimeError('The default mime type could not be found in the registered templates.')
    
        response = render_to_response(desired_template, context, **kwargs)
        response['Content-Type'] = "%s; charset=%s" % (content_type, settings.DEFAULT_CHARSET)
        return response
