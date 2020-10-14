from scrapy import Field, Item


class TeacherItem(Item):
    name = Field()
    rank = Field()
    ext = Field()
    section = Field()
    email = Field()
    url = Field()
    image_data = Field()
    image_ext = Field()
    origin = Field()
