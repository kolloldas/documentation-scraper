from serializers.document_serializer import DocumentSerializer
import json

class BasicSerializer(DocumentSerializer):
    """
    A basic serializer. Saves everything as JSON
    """
    def __init__(self, url, documentation_parser, save_path=''):
        super(BasicSerializer, self).__init__(url, documentation_parser, 'json', save_path=save_path)

    def convert(self, doc, url, fname):
        content = {
            'name': doc.name,
            'url': url,
            'object_type': doc.object_type,
            'summary': doc.summary,
            'api_level': doc.api_level,
            'parent_class': doc.parent_class,
            'interfaces': doc.interfaces,
            'nested_classes': doc.nested_classes,
            'constants': doc.constants,
            'fields': doc.fields,
            'constructors': doc.constructors,
            'public_methods': doc.public_methods,
            'protected_methods': doc.protected_methods

        }

        return json.dumps(content)