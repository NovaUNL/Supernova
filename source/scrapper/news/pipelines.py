from news.models import NewsItem


class NewsItemPipeline(object):
    def process_item(self, item, spider):
        current = NewsItem.objects.filter(
            title=item['title'],
            datetime=item['datetime'],
            generated=True).first()
        if current is not None:
            new_content = item['content']
            if current.content == new_content:
                item.save(commit=False)
            else:
                current.content = new_content
                current.save()
            current.gen_summary()
        else:
            item.save()
        return item
