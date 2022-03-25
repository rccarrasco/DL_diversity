import sys, re
from xml.sax.handler import ContentHandler
from xml.sax import make_parser
from io import StringIO
import gzip

class MARC_Handler(ContentHandler):
    """
    SAX call backsfor thr following MARC fields
        001: record identifier
        008: record information (NR = non-repeatable, starts with year)
        010 $a: LoC record identifier (NR)
        100 $a $d: main author name and dates (NR)
        650: topical term (R = repeatable)   
        920: $a UGent record type
    """
    patterns = {
        '001':re.compile(r'\D*(\d+)\b'),
        '005': re.compile(r'(\d{4})\d{10}\.\d'),
        '008': re.compile(r'(\w\w)\w+'),
        '010': re.compile(r'\D*(\d+)\b')
        }
    
    # return relevant content in field labeled with the specified tag
    @staticmethod
    def _parse_(tag, text):
        m = MARC_Handler.patterns[tag].match(text)
        if m:
            return m.group(1)
        else:
            print(f'Invalid content in controlfield {tag}: {text}', 
                  file=sys.stderr)
            return ''
        
    def __init__(self, target):
        self.target = target
        self.num_records = 0
        self.tag = None
        self.content = StringIO()
        
        
    # return textual content and reset text buffer
    def getvalue(self):
        text = self.content.getvalue()
        self.content.truncate(0)
        self.content.seek(0)
        
        return text
        
    # reset record variables
    def reset(self):
        # main variables
        self.record_id = ''
        self.year = ''
        self.author = ''
        self.topics = list()
        self.type = '*'
        
        # auxiliary variables (field tag and subfields)
        self.tag = None
        self.subfields = None
        
    def __str__(self):
        return '\t'.join((self.record_id, 
                          str(self.year), 
                          self.author, 
                          '@'.join(self.topics), self.type))
        
        
    # opening a new XML element
    def startElement(self, name, attrs):
        if name == 'record':
            self.reset()
        elif name == 'controlfield':
            self.tag = attrs.get('tag')
            self.subfields = None
        elif name == 'datafield':
            self.tag = attrs.get('tag')
            self.subfields = list()
        elif name == 'subfield' and self.tag in ('010', '100', '650', '920'):
            self.code = attrs.get('code')
            
            
    # save content to buffer (for efficiencly, only for selected fields)
    def characters(self, text):
        if self.tag in ('001', '008', '010', '100', '650', '920') :
            self.content.write(text.strip())
      
    # closing an XML element
    def endElement(self, name):
        if name == 'record':
            print(self, file=self.target)
            self.num_records += 1
            if self.num_records % 100000 == 0:
                print(f'{self.num_records // 1000}K records', file=sys.stderr)
        elif name == 'controlfield':
            if self.tag == '001':
                self.record_id = self._parse_(self.tag, self.getvalue())
            elif self.tag == '008':
                year = int(self._parse_(self.tag, self.getvalue()))
                if year < 100:
                    self.year = 2000 + year if year < 30 else 1900 + year
                else:
                    self.year = year
        elif name == 'datafield':
            if self.tag == '100':
                self.author = ' '.join(self.subfields)
            elif self.tag == '650':
                self.topics.append('--'.join(self.subfields))
        elif name == 'subfield':
            content = self.getvalue()
            if self.tag == '010' and self.code == 'a':
                if self.record_id == '':
                    self.record_id = self._parse_(self.tag, content)
            elif self.tag == '100' and self.code in ('a', 'd'):
                self.subfields.append(content.replace('.', ' ').strip())
            elif self.tag == '650' and self.code.isalpha():
                self.subfields.append(content.replace('.', ' ').strip())
            elif self.tag == '920' and self.code == 'a':
                self.type = content.strip()
                
class MARC_Parser(object):
    """
    Parse a MARC-XML file and extract relevant fields as CSV records
    """
    def __init__(self):   
        self.sax_parser = make_parser()   
   
    @staticmethod
    def print_header(target):
        heads = ('RECORD_ID', 'YEAR', 'MAIN_AUTHOR', 'SUBJECT_HEADINGS', 'TYPE')
        print('\t'.join(heads), file=target)
        
    
    def parse_to_file(self, filename):    
        """
        Parse XML to CSV file with same name and CSV extension.

        Parameters
        ----------
        filename : str
            The input filename.

        Raises
        ------
        NotImplementedError
            If the input file format is not supported.
        """
        if filename.endswith('.xml'):
            source = open(filename)
            target = open(filename.replace('.xml','.csv'), 'w')
        elif filename.endswith('.xml.gz'):
            source = gzip.open(filename)
            target = open(filename.replace('.xml.gz','.csv'), 'w')
        else:
           raise NotImplementedError('File with unparsable extension', filename)
     
        handler = MARC_Handler(target)
        self.sax_parser.setContentHandler(handler)       
        MARC_Parser.print_header(target)
        self.sax_parser.parse(source)
        
    def parse(self, filename):
        """
        Parse XML and print CSV output to stdout.

        Parameters
        ----------
        filename : str
            The input filename.

        Raises
        ------
        NotImplementedError
            If the input file format is not supported.
        """
        if filename.endswith('.xml'):
            source = open(filename)
        elif filename.endswith('.xml.gz'):
            source = gzip.open(filename)
        else:
           raise NotImplementedError('File with unparsable extension', filename)
        handler = MARC_Handler(sys.stdout)
        self.sax_parser.setContentHandler(handler)       
        self.sax_parser.parse(source)
        
        
  
if __name__ == '__main__':
    if len(sys.argv)  > 1:
        parser = MARC_Parser()
        if sys.argv[1] == '-f':
            for filename in sys.argv[2:]:
                parser.parse_to_file(filename)
        else:
            MARC_Parser.print_header(sys.stdout)
            for filename in sys.argv[1:]:
                parser.parse(filename)
                
       
