from documentation import Documentation
import re

class DocumentationParser(object):
    """
    Base class for documentation parsers
    """
    def __init__(self, soup):
        self._soup = soup
        self._documentation = Documentation()

    def extract(self):
        return self.parse(self._soup, self._documentation)

    def parse(self, soup, doc):
        raise NotImplementedError()

    @property
    def documentation(self):
        return self._documentation



