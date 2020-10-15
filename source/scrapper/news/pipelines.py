import io
import logging

from django.core.files import File
from django.db.models import Q

from news.models import NewsItem


class NewsItemPipeline(object):
    def process_item(self, item, spider):
        image = item.get('image_data', None)
        image_filename = item.get('image_filename', None)

        current = NewsItem.objects.filter(
            Q(title=item['title'], datetime=item['datetime']) | Q(source=item['source']), generated=True).first()
        if current is not None:
            print(f"{item['title']} - {item['datetime']}\n"
                  f"\t {item['source']} {item.get('image_filename', None)}\n\tCurrent: {current} {current.cover_img}")
        if current is None:
            current = NewsItem(
                title=item['title'],
                datetime=item['datetime'],
                source=item['source'],
                content=item['content'],
                generated=True,
            )
        else:
            current.content = item['content']

        if image_filename is not None:
            if image is None:
                logging.error("Inconsistency. Image name but no image.")
                return
            current.cover_img.save(image_filename, File(io.BytesIO(image)))

        current.gen_summary()
        current.save()
        return item
