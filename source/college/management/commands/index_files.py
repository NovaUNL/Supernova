import logging
import queue
import datetime
import traceback
from io import StringIO
from multiprocessing import Process
from multiprocessing import Queue


from elasticsearch import Elasticsearch

from django.core.management.base import BaseCommand
from django.conf import settings

from college import models as college
from scrapper.files import pdfplumber_parse

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
        file_path = f"{settings.EXTERNAL_ROOT}/{file_hash[:2]}/{file_hash[2:]}"
        try:
            document_data = pdfplumber_parse(file_path, file_hash)
            if document_data is not None:
                output.put(document_data)
        except Exception as e:
            print(f"File {file_hash} had an exception: {e}")
            traceback.print_exc()


