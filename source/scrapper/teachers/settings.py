BOT_NAME = 'teachers-'

SPIDER_MODULES = ['scrapper.teachers']
NEWSPIDER_MODULE = 'scrapper.teachers'

ROBOTSTXT_OBEY = True

LOG_LEVEL = 'INFO'

ITEM_PIPELINES = {
    'scrapper.teachers.pipelines.TeacherPipeline': 300,
}
