import io

from django.core.files import File

from news.models import NewsItem


class NewsItemPipeline(object):
    def process_item(self, item, spider):
        image = item.get('image_data', None)
        image_filename = item.get('image_filename', None)
        current = NewsItem.objects.filter(
            title=item['title'],
            datetime=item['datetime'],
            generated=True).first()
        if current is None:
            current = NewsItem(
                title=item['title'],
                datetime=item['datetime'],
                source=item['source'],
                generated=True,
            )
        else:
            current.content = item['content']

        current.gen_summary()
        current.save()
        if image is not None:
            current.cover_img.save(image_filename, File(io.BytesIO(image)))
        return item
