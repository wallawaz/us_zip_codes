class BaseScraper:
    def __init__(self, search_page, **kwargs):
        self.search_page = search_page
        self.kwargs = kwargs
