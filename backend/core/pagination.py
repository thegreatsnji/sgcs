"""Paginação padronizada da API."""

from rest_framework.pagination import PageNumberPagination

from core.constants import DEFAULT_PAGE_SIZE


class StandardPagination(PageNumberPagination):
    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = 100
