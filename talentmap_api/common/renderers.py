'''
Modified from https://github.com/mjumbewu/django-rest-framework-csv
Supports CSV rendering on paginated views
'''

from rest_framework_csv.renderers import CSVRenderer


class PaginatedCSVRenderer (CSVRenderer):
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
