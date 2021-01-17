import logging
import datetime
import traceback
from io import StringIO

from pdfminer import pdfparser, pdfdocument
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.layout import LTFigure, LTImage, LAParams
import pdfplumber
from bs4 import UnicodeDammit

logging.getLogger("pdfminer").setLevel(logging.WARNING)

PARSER_VERSION = 0


def parse(file_path, file_hash):
    data = pdfplumber_parse(file_path, file_hash)
    if data:
        data['version'] = PARSER_VERSION


def pdfplumber_parse(file_path, file_hash):
    pages = []
    links = []
    images = []
    width = 0
    height = 0

    try:
        with pdfplumber.open(file_path) as pdf:
            print(f"Processing {file_path}")
            meta = pdf.metadata
            pages_cont = len(pdf.pages)
            if pages_cont > 300:
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
                    print(f"Exception in page {i} of {file_hash}: {e}")
                    traceback.print_exc()
                # for image in page.images:
                #     im = Image.frombytes(
                #         mode="1",
                #         data=image['stream'].get_data(),
                #         size=image['srcsize'],
                #         decoder_name='raw')
                # page = page.dedupe_chars(tolerance=1)
                _text = page.extract_text()
                if _text is not None:
                    pages.append(_text)
            print(f"Ended processing {file_path}")
    except pdfparser.PDFSyntaxError:
        raise Exception(f"{file_hash} is not a PDF")  # TODO proper exception
    except pdfdocument.PDFPasswordIncorrect:
        return None
    except Exception as e:
        raise Exception(f"{file_hash} had exception {e}")  # TODO proper exception

    return {
        'hash': file_hash,
        'pages': pages,
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
                # for element in layout:
                #     if isinstance(element, LTImage):
                #         print()
                #     elif isinstance(element, LTFigure):
                #         print()
                # TODO Complete
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
