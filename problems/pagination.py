from rest_framework.pagination import PageNumberPagination


class ProblemNumPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "size"
    max_page_size = 40
