from rest_framework.pagination import PageNumberPagination


class ControllablePageNumberPagination(PageNumberPagination):
    # Query parameter for the page number
    page_query_param = "page"

    # Default page size
    page_size = 100
    max_page_size = 1000

    # Query parameter for the page size limit
    page_size_query_param = "limit"

    # Strings if used as the page number will give you the final page
    last_page_strings = ("last", "final", "end")
