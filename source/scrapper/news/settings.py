BOT_NAME = 'news-'

SPIDER_MODULES = ['scrapper.news']
NEWSPIDER_MODULE = 'scrapper.news'

ROBOTSTXT_OBEY = True

LOG_LEVEL = 'INFO'

ITEM_PIPELINES = {
    'scrapper.news.pipelines.NewsItemPipeline': 300,
}
