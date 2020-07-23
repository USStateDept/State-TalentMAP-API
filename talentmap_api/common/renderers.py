from django import forms
from django.core.paginator import Page

from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.request import override_method
from rest_framework_csv.renderers import CSVRenderer


class PaginatedCSVRenderer(CSVRenderer):
    '''
    Modified from https://github.com/mjumbewu/django-rest-framework-csv
    Supports CSV rendering on paginated views
    '''
    results_field = 'results'

    def render(self, data, *args, **kwargs):
        '''
        We need the handle the following cases:
            1. Paginated endpoint
                 {
                    page_metadata
                    results: [<RENDERABLES>]
                 }
            2. Non-paginated list endpoints
                [<RENDERABLES>]
            3. Single-object retrieve endpoints
                <RENDERABLE>
        '''

        '''
        In case 2, we don't need to do anything
        In cases 1 & 3, the data is not a list, so we check for that here
        '''
        if not isinstance(data, list):
            '''
            In case 1, we have a data[results_field] array, so that is returned
            In case 3, we don't, so we hit the default of creating an array with
            a single item, the retrieved object
            '''
            data = data.get(self.results_field, [data])
        return super(PaginatedCSVRenderer, self).render(data, *args, **kwargs)


class BrowsableAPIRendererWithoutForms(BrowsableAPIRenderer):
    """Renders the browsable api, but excludes the HTML form."""

    def get_rendered_html_form(self, data, view, method, request):
        """Don't render the HTML form"""
        return None

    # Lifted from the DRF, but modified to remove content + HTML form
    def get_raw_data_form(self, data, view, method, request):
        """
        Returns a form that allows for arbitrary content types to be tunneled
        via standard HTML forms.
        (Which are typically application/x-www-form-urlencoded)
        Modifications: Set content to None so this doesn't bombard the database
        """
        serializer = getattr(data, 'serializer', None)
        if serializer and not getattr(serializer, 'many', False):
            instance = getattr(serializer, 'instance', None)
            if isinstance(instance, Page):
                instance = None
        else:
            instance = None

        with override_method(view, request, method) as request:
            # Check permissions
            if not self.show_form_for_method(view, method, request, instance):
                return

            # Generate a generic form that includes a content type field,
            # and a content field.
            media_types = [parser.media_type for parser in view.parser_classes]

            class GenericContentForm(forms.Form):
                _content_type = forms.ChoiceField(
                    label='Media type',
                    choices=[(media_type, media_type) for media_type in media_types],
                    initial=media_types[0],
                    widget=forms.Select(attrs={'data-override': 'content-type'})
                )
                _content = forms.CharField(
                    label='Content',
                    widget=forms.Textarea(attrs={'data-override': 'content'}),
                    initial=None
                )

            return GenericContentForm()
