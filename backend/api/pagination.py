from rest_framework.pagination import PageNumberPagination


class PagesPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = 6
