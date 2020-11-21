from django.core.management.base import BaseCommand
import logging
import datetime
from pdfminer import pdfparser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
import pdfminer.high_level
import pdfminer.layout
from elasticsearch import Elasticsearch
from bs4 import UnicodeDammit
from college import models as college


logging.basicConfig()
logging.getLogger("pdfminer").setLevel(logging.WARNING)


class Command(BaseCommand):

    def handle(self, *args, **options):
        i = 1
        elastic = Elasticsearch()
        elastic.indices.create(index='document_data', ignore=400)
        for file in college.File.objects.filter(external=True, mime='application/pdf').all():
            results = elastic.search(
                index='document_data',
                body={
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"hash": file.hash}},
                                # Deduplication criteria, perhaps?
                            ]
                        }
                    }
                }, ignore=400)
            hits = results['hits']['hits']

            if 'error' in results or len(hits) == 0:
                file_path = f"/files/{file.hash[:2]}/{file.hash[2:]}"
                with open(file_path, 'rb') as fp:
                    parser = PDFParser(fp)
                    doc = PDFDocument(parser)
                try:
                    text = pdfminer.high_level.extract_text(file_path, codec='utf-8')
                    document_meta = {
                        'hash': file.hash,
                        'text': text,
                        'meta': flaten_and_unicode(doc.info)
                    }
                    indexed = elastic.index(index='document_data', body=document_meta, op_type='index')
                    print(f"{i} - {datetime.datetime.now()}")
                    i += 1
                except pdfparser.PDFSyntaxError:
                    print(f"{file.hash} is not a PDF")
                except Exception as e:
                    print(f"{file.hash} had exception {e}")
            elif len(hits) > 1:
                raise Exception()
            else:
                pass


def flaten_and_unicode(data):
    result = dict()
    for subinfo in data:
        for (key, value) in subinfo.items():
            if isinstance(value, bytes):
                try:
                    unicode_value = UnicodeDammit(value).unicode_markup.strip()
                except Exception as e:
                    continue
                if unicode_value != '':
                    result[key] = unicode_value
            elif isinstance(value, list):
                if len(value) > 1:
                    pass
                unicode_value = []
                if (all(map(lambda subval: isinstance(value, bytes), value))):
                    for subval in value:
                        try:
                            unicode_subval = UnicodeDammit(subval).unicode_markup.strip()
                            if unicode_subval != '':
                                unicode_value.append(unicode_subval)
                        except Exception as e:
                            pass

                if len(unicode_value) > 0:
                    result[key] = unicode_value
            # else:
            #     print(f"Subinfo with an unknown type {value}")
    return result
