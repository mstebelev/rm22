import codecs
import csv
import re
import StringIO

from itertools import groupby
from operator import itemgetter

from django.core.serializers.python import Serializer as PythonSerializer
from django.core.serializers.python import Deserializer as PythonDeserializer
from django.utils.encoding import smart_unicode


class Serializer(PythonSerializer):
    """
    Convert a queryset to CSV.
    """
    internal_use_only = False

    def end_serialization(self):

        def process_item(item):
            if isinstance(item, (list, tuple)):
                item = process_m2m(item)
            elif isinstance(item, bool):
                item = str(item).upper()
            elif isinstance(item, basestring):
                if item in ('TRUE', 'FALSE', 'NULL') or _LIST_RE.match(item):
                    # Wrap these in quotes, so as not to be confused with
                    # builtin types when deserialized
                    item = "'%s'" % item
            elif item is None:
                item = 'NULL'
            return smart_unicode(item)

        def process_m2m(seq):
            parts = []
            for item in seq:
                if isinstance(item, (list, tuple)):
                    parts.append(process_m2m(item))
                else:
                    parts.append(process_item(item))
            return '[%s]' % ', '.join(parts)

        writer = UnicodeWriter(self.stream, encoding='utf-8')
        # Group objects by model and write out a header and rows for each.
        # Multiple models can be present when invoking from the command
        # line, e.g.: `python manage.py dumpdata --format csv auth`
        for k, g in groupby(self.objects, key=itemgetter('model')):
            write_header = True
            for d in g:
                # "flatten" the object. PK and model values come first,
                # then field values. Flat is better than nested, right? :-)
                pk, model, fields = d['pk'], d['model'], d['fields']
                pk, model = smart_unicode(pk), smart_unicode(model)
                row = [pk, model] + map(process_item, fields.values())
                if write_header:
                    header = ['pk', 'model'] + fields.keys()
                    writer.writerow(header)
                    write_header = False
                writer.writerow(row)

    def getvalue(self):
        if callable(getattr(self.stream, 'getvalue', None)):
            return self.stream.getvalue()

_QUOTED_BOOL_NULL = """ 'TRUE' 'FALSE' 'NULL' "TRUE" "FALSE" "NULL" """.split()

# regular expressions used in deserialization
_LIST_PATTERN = r'\[(.*)\]'
_LIST_RE = re.compile(r'\A%s\Z' % _LIST_PATTERN)
_QUOTED_LIST_RE = re.compile(r"""
    \A                 # beginning of string
    (['"])             # quote char
    %s                 # list
    \1                 # matching quote
    \Z                 # end of string""" % _LIST_PATTERN, re.VERBOSE)
_SPLIT_RE = re.compile(r', *')
_NK_LIST_RE = re.compile(r"""
    \A                 # beginning of string
    \[                 # opening bracket
    [^]]+              # one or more non brackets
    \]                 # closing bracket
    (?:, *\[[^]]+\])*  # zero or more of above, separated
                       #   by a comma and optional spaces
    \Z                 # end of string""", re.VERBOSE)
_NK_SPLIT_RE = re.compile(r"""
    (?<=\])            # closing bracket (lookbehind)
    , *                # comma and optional spaces
    (?=\[)             # opening bracket (lookahead)""", re.VERBOSE)

class UnicodeWriter(object):
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding='utf-8', **kwds):
        # Redirect output to a queue
        self.queue = StringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode('utf-8') for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode('utf-8')
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
