from serializers.document_serializer import DocumentSerializer
from urllib.parse import urlparse
import os
import json
import re

class DrQASerializer(DocumentSerializer):
    """
    A serializer that saves documents in a format compatible with Facebook's DrQA system
    """
    def __init__(self, url, documentation_parser, save_path=''):
        super(DrQASerializer, self).__init__(url, documentation_parser, 'txt', save_path=save_path)

    def convert(self, doc, url, fname):
        path = urlparse(url).path
        path, _ = os.path.splitext(path)

        name = re.sub(r'/', '.', path)

        prefix = name[1:] #doc.name or fname
        contents = []

        if doc.summary:
            summary = {
                "id": prefix + ' Summary',
                "url": url,
                "text": '\n'.join(doc.summary)
            }
            contents.append(json.dumps(summary))
        
        def add_value_text(items, header):
            items_text = [item['name'] + ' is ' + item['description'] for item in items]
            item_dict = {
                "id": prefix + ' ' + header,
                "url": url,
                "text": '\n'.join(items_text)
            }
            contents.append(json.dumps(item_dict))

        def add_method_text(items, header):
            items_text = [item['name'] + ' ' + item['description'] for item in items]
            item_dict = {
                "id": prefix + ' ' + header,
                "url": url,
                "text": '\n'.join(items_text)
            }
            contents.append(json.dumps(item_dict))
        
        if doc.constants:
            add_value_text(doc.constants, 'Constants')

        if doc.fields:
            add_value_text(doc.fields, 'Fields')

        if doc.constructors:
            add_method_text(doc.constructors, 'Constructors')
        
        if doc.public_methods:
            add_method_text(doc.public_methods, 'Public methods')

        if doc.protected_methods is not None:
            add_method_text(doc.protected_methods, "Protected methods")

        return '\n'.join(contents)