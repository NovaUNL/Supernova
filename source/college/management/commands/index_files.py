import logging
import queue
import traceback
from io import StringIO
from multiprocessing import Process
from multiprocessing import Queue

from django.core.management.base import BaseCommand
import datetime
from pdfminer import pdfparser, pdfdocument
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.layout import LTFigure, LTImage, LAParams
import pdfplumber
from bs4 import UnicodeDammit
from PIL import Image
from elasticsearch import Elasticsearch
from college import models as college

logging.basicConfig()
logging.getLogger("pdfminer").setLevel(logging.WARNING)
es_logger = logging.getLogger('elasticsearch')
es_logger.propagate = False
es_logger.setLevel(logging.WARNING)

PROCESS_COUNT = 4


class Command(BaseCommand):

    def handle(self, *args, **options):
        input_queue = Queue()  # File hashes
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
                                # More deduplication criteria, perhaps?
                            ]
                        }
                    }
                }, ignore=400)
            hits = results['hits']['hits']

            if 'error' in results or len(hits) == 0:
                input_queue.put(file.hash)

        i = 1
        processes = []
        output_queue = Queue()

        for _ in range(PROCESS_COUNT):
            p = Process(target=process_exec, args=(input_queue, output_queue))
            p.start()
            processes.append(p)

        while True:  # output_queue.qsize() > 0 or any(map(lambda p: p.is_alive(), processes)):
            try:
                document_data = output_queue.get(timeout=30)
                indexed = elastic.index(index='document_data', body=document_data, op_type='index')
                print(f"{i} - {datetime.datetime.now()}")
                i += 1
            except Exception:  # queue.Empty:
                pass


def process_exec(input: Queue, output: Queue):
    while input.qsize() > 0:
        file_hash = input.get()
        file_path = f"/s/clipy/files/{file_hash[:2]}/{file_hash[2:]}"
        try:
            document_data = pdfplumber_parse(file_path, file_hash)
            if document_data is not None:
                output.put(document_data)
        except Exception as e:
            print(f"File {file_hash} had an exception: {e}")
            traceback.print_exc()


def pdfplumber_parse(file_path, file_hash):
    text = []
    links = []
    images = []
    width = 0
    height = 0

    try:
        with pdfplumber.open(file_path) as pdf:
            meta = pdf.metadata
            if len(pdf.pages) > 300:
                print(f"Skipped {file_hash}")
                return None
            for i, page in enumerate(pdf.pages):
                if i == 0:
                    width = page.width
                    height = page.height
                try:
                    for link in page.hyperlinks:
                        links.append(link['uri'])
                except Exception as e:
                    print(e)
                # for image in page.images:
                #     im = Image.frombytes(
                #         mode="1",
                #         data=image['stream'].get_data(),
                #         size=image['srcsize'],
                #         decoder_name='raw')
                page = page.dedupe_chars(tolerance=1)
                _text = page.extract_text()
                if _text is not None:
                    text.append(_text)
    except pdfparser.PDFSyntaxError:
        print(f"{file_hash} is not a PDF")
        return None


    return {
        'hash': file_hash,
        'text': "\n".join(text),
        'links': links,
        'images': images,
        'meta': meta,
        'width': width,
        'height': height,
    }


def pdfminer_parse(file_path, file_hash):
    output_string = StringIO()
    try:
        with open(file_path, 'rb') as fp:
            parser = PDFParser(fp)
            doc = PDFDocument(parser)

            laparams = LAParams()
            rsrcmgr = PDFResourceManager(caching=True)
            txt_device = TextConverter(rsrcmgr, output_string, codec='utf-8', laparams=laparams)
            aggr_device = PDFPageAggregator(rsrcmgr, laparams=laparams)
            txt_interpreter = PDFPageInterpreter(rsrcmgr, txt_device)
            aggr_interpreter = PDFPageInterpreter(rsrcmgr, aggr_device)
            from pdfminer.high_level import extract_pages
            extract_pages("test.pdf")
            for page in PDFPage.get_pages(fp, caching=True):
                txt_interpreter.process_page(page)
                aggr_interpreter.process_page(page)
                layout = aggr_device.get_result()
                for element in layout:
                    if isinstance(element, LTImage):
                        print()
                    elif isinstance(element, LTFigure):
                        print()
                # Complete
    except pdfparser.PDFSyntaxError:
        print(f"{file_hash} is not a PDF")
        return None

    return {
        'hash': file_hash,
        'text': output_string.getvalue(),
        'meta': flatten_and_unicode(doc.info)
    }


def flatten_and_unicode(data):
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
