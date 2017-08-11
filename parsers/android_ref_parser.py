from parsers.documentation_parser import DocumentationParser
import re


def _ws_mapping_fn(match):
        if ' ' in match.group(0):
            return ' '
        else:
            return ''

def _get_text_cleaned(block):
    return re.sub('\n+|\s+', _ws_mapping_fn, block.get_text().strip())

class AndroidDocParser(DocumentationParser):
    """
    Parser for android documentation on https://developer.android.com
    """
    def _get_name_level(self, block):
        m = re.search(r'apilevel-(.*)', block['class'][-1])
        api_level = m.group(1) if m else '1'
        
        if block.h3:
            name = _get_text_cleaned(block.h3) 
        elif block.h1:
            name = _get_text_cleaned(block.h1)
        else:
            name = None 

        return name, api_level


    def process_nested_classes(self, block, doc):
        if block.name == 'table' and block.has_attr('id') and 'nestedclasses' in block['id']:

            for table_row in block.find_all('tr'):
                cells = table_row.find_all('td')
                if len(cells) > 0:
                    class_interface = _get_text_cleaned(cells[0].code)
                    name = _get_text_cleaned(cells[1].code)
                    type_dec = _get_text_cleaned(cells[1].p)
                    doc.add_nested_class(name, class_interface, type_dec)


    def process_class_summary(self, block, doc):
        if block.name == 'h1' and block.has_attr('class') and 'api-title' in block['class']:
            doc.set_name(_get_text_cleaned(block))
            
            p = block.find_next_sibling('p')
            if p and p.code and p.code.has_attr('class') and 'api-signature' in p.code['class']:
                signature = _get_text_cleaned(p.code)
                m = re.search(r'(?:public|private|protected)\s(?:static\s)?(?:abstract\s)?(interface|class)\s\S+', signature)
                if m:
                    doc.set_object_type(m.group(1))
            if p:
                for code in p.find_all('code', class_='api-signature'):
                    if 'extends' in code.text:
                        item = code.find('a')
                        if item:
                            doc.set_parent_class(_get_text_cleaned(item))
                    elif 'implements' in code.text:
                        items = code.find_all('a')
                        if items:
                            doc.set_interfaces([_get_text_cleaned(item) for item in items])
        
        if block.name == 'p':
            # Remove class signature
            if block.find('code', {'class': 'api-signature'}):
                return
            doc.append_summary(_get_text_cleaned(block))
        elif block.name == 'ul':
            doc.append_summary(_get_text_cleaned(block))


    def process_constants(self, block, doc):
        if block.name == 'div' and 'api' in block['class']:
            const_name, api_level = self._get_name_level(block)
            
            sig_block = block.find('pre')
            m = re.search(r'(\S+?)\s', sig_block.get_text())
            const_type = m.group(0)
            
            desc_block = sig_block.find_next('p')
            const_description = _get_text_cleaned(desc_block)
            value_block = desc_block.find_next('p', text = re.compile(r'.*[cC]onstant.*'))
            const_value = _get_text_cleaned(value_block)

            doc.add_constant(const_name, const_type, const_value, const_description, api_level)



    def process_fields(self, block, doc):
        if block.name == 'div' and 'api' in block['class']:
            field_name, api_level = self._get_name_level(block)

            sig_block = block.find('pre')
            m = re.search(r'(\S+?)\s', sig_block.get_text())
            field_type = m.group(0)
            
            desc_block = sig_block.find_next('p')
            field_description = _get_text_cleaned(desc_block)

            doc.add_field(field_name, field_type, field_description, api_level)


    def process_methods(self, block, doc, section):
        if block.name == 'div' and 'api' in block['class']:
            method_name, api_level = self._get_name_level(block)
            
            #Method description
            desc_block = block.find('p')
            method_description = _get_text_cleaned(desc_block)

            if section == 'Public methods':
                params, returns = doc.add_public_method(method_name, method_description, api_level)
            elif section == 'Protected methods':
                params, returns = doc.add_protected_method(method_name, method_description, api_level)
            elif section == 'Public constructors':
                params, returns = doc.add_constructor(method_name, method_description, api_level)
            else:
                return
            
            #Method parameters
            param_return_block = desc_block.find_next_sibling('table')
            
            if param_return_block:
                header_row = param_return_block.find('tr')
                if header_row.th and 'Parameters' in header_row.th.get_text():
                    for table_row in header_row.find_next_siblings('tr'):
                        #print(table_row)
                        cells = table_row.find_all('td')
                        if len(cells) > 0:
                            param_name = _get_text_cleaned(cells[0].code)
                            param_type = _get_text_cleaned(cells[1].code)
                            param_desc = _get_text_cleaned(cells[1])
                            params.add(param_name, param_type, param_desc)

                    param_return_block = param_return_block.find_next('table')
            
            # Method return type
            method_return_type = 'void' #default
            method_return_desc = None
            if param_return_block:
                header_row = param_return_block.find('tr')
                if header_row.th and 'Returns' in header_row.th.get_text():
                    cells = param_return_block.find_all('td')
                    method_return_type = _get_text_cleaned(cells[0].code)
                    method_return_desc = _get_text_cleaned(cells[1])
                    returns.set_returns(method_return_type, method_return_desc)
            
    
    def update_section(self, block, cur_section):
        new_section = cur_section
        if block.name == 'a' and block.h2: #Edge case
            block = block.h2
            
        if block.name == 'h2' and block.has_attr('class') and 'api-section' in block['class']:
            if block.text in ['Constants', 'Fields', 'Public constructors', 'Protected constructors',
                              'Public methods', 'Protected methods']:
                new_section = block.text
        return new_section
    
    def process_tree(self, tree, doc):
        section = 'Class Summary'
        for block in tree:
            section = self.update_section(block, section)
            if section == 'Class Summary':
                self.process_class_summary(block, doc)
            elif section == 'Constants':
                self.process_constants(block, doc)
            elif section == 'Fields':
                self.process_fields(block, doc)
            elif section in ['Public methods', 'Protected methods', 'Public constructors']:
                self.process_methods(block, doc, section)
        
            # Only found in table
            self.process_nested_classes(block, doc)

    def parse(self, soup, doc):
        tree = soup.find('div', class_="api")
        if not tree:
            return False

        _, api_level = self._get_name_level(tree)
        doc.set_api_level(api_level)

        self.process_tree(tree, doc)

        return True
