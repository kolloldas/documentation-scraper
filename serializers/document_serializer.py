from urllib.parse import urlparse
import os


class DocumentSerializer(object):
    """
    Base class for document serializers
    """
    def __init__(self, url, documentation_parser, file_ext, save_path=''):
        self._parser = documentation_parser
        self._url = url
        self._file_ext = file_ext
        self._save_path = save_path

    def _create_path(self):
        p = urlparse(self._url)
        reldir, html_filename = os.path.split(p.path)
        dir = os.path.join(self._save_path, reldir[1:])
        os.makedirs(dir, exist_ok=True)
        fname, ext = os.path.splitext(html_filename)

        path = os.path.join(dir, fname + '.' + self._file_ext)
        return path, fname
    
    def convert(self, doc, url, fname):
        raise NotImplementedError()

    def save(self):
        path, fname = self._create_path()
        text = self.convert(self._parser.documentation, self._url, fname)
        if len(text.strip()) > 10:
            with open(path, 'w') as fp:
                fp.write(text)

