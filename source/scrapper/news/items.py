from scrapy import Field, Item


class NewsItemItem(Item):
    title = Field()
    source = Field()
    content = Field()
    datetime = Field()
    image_data = Field()
    image_filename = Field()
