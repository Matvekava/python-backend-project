from rest_framework.pagination import PageNumberPagination

class CardPagination(PageNumberPagination):
    page_size = 10                     # количество записей на страницу по умолчанию
    page_size_query_param = 'page_size'  # разрешить клиенту менять размер через ?page_size=...
    max_page_size = 100