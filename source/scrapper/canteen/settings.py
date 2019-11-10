BOT_NAME = 'canteen-'

SPIDER_MODULES = ['scrapper.canteen']

ROBOTSTXT_OBEY = True


LOG_LEVEL = 'INFO'

ITEM_PIPELINES = {
   'scrapper.canteen.pipelines.CanteenPipeline': 300,
}