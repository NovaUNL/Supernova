import hashlib
import logging
import traceback
from io import StringIO

from pdfminer import pdfparser, pdfdocument
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.layout import LTFigure, LTImage, LAParams
import fitz
import pdfplumber
from bs4 import UnicodeDammit

logging.getLogger("pdfminer").setLevel(logging.WARNING)


def parse(file_path, file_hash):
    parser_data = {}
    data = {
        'parsers': parser_data
    }
    pymu_data = pymu_parse(file_path)
    parser_data['pymu'] = {
        'revision': 2020121,
        'data': pymu_data
    }
    if pymu_data:
        data['pages'] = list(map(lambda p: p['text'], pymu_data['pages']))
        data['links'] = list(
            set([link for page_links in map(lambda p: p['links'], pymu_data['pages']) for link in page_links]))
    else:
        return None
    plumber_data = pdfplumber_parse(file_path, file_hash)
    parser_data['plumber'] = {
        'revision': 2020121,
        'data': plumber_data
    }
    return data


def pdfplumber_parse(file_path, file_hash):
    pages = []
    links = []

    try:
        with pdfplumber.open(file_path) as pdf:
            meta = pdf.metadata
            pages_cont = len(pdf.pages)
            if pages_cont > 300:
                return None
            for i, page in enumerate(pdf.pages):
                page_links = []
                try:
                    for link in page.hyperlinks:
                        links.append(link['uri'])
                        page_links.append(link['uri'])
                except UnicodeDecodeError:
                    pass
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
                text = page.extract_text()
                if text is None:
                    text = ''

                pages.append({
                    'text': text,
                    'links': page_links,
                    'width': int(page.width),
                    'height': int(page.height)})
            print(f"Ended processing {file_path}")
    except pdfparser.PDFSyntaxError:
        raise Exception(f"{file_hash} is not a PDF")  # TODO proper exception
    except pdfdocument.PDFPasswordIncorrect:
        return None
    except Exception as e:
        raise Exception(f"{file_hash} had exception {e}")  # TODO proper exception

    return {
        'pages': pages,
        'links': links,
        'meta': meta,
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
        'text': output_string.getvalue(),
        'meta': flatten_and_unicode(doc.info)
    }


def pymu_parse(file_path):
    try:
        doc = fitz.open(file_path)
    except RuntimeError:
        return None

    if not doc.isPDF:
        return

    try:
        toc = doc.get_toc()
    except ValueError:
        return
    pages = []
    for page in doc:
        links = []
        for link in page.getLinks():
            uri = link.get('uri')
            if uri:
                links.append(uri)
                continue

            file = link.get('file')
            if file:
                links.append('file:' + file)
                continue
        pages.append({
            'text': page.getText('text'),
            # 'structure': page.getText('dict'),
            'links': links,
            # 'annotations': list(page.annots()),
            'width': int(page.MediaBoxSize.x),
            'height': int(page.MediaBoxSize.y),
            'content_hash': hashlib.sha1(page.read_contents()).hexdigest(),
            'visual_hash': hashlib.sha1(page.getPixmap().samples).hexdigest()})

    return {
        'pages': pages,
        'pages_count': doc.pageCount,
        'meta': doc.metadata,
        'toc': toc,
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
