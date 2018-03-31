from django.contrib import admin

from synopses.models import Area, Subarea, Topic, Section, ClassSection, SectionTopic, SectionLog

admin.site.register(Area)
admin.site.register(Subarea)
admin.site.register(Topic)
admin.site.register(Section)
admin.site.register(ClassSection)
admin.site.register(SectionTopic)
admin.site.register(SectionLog)
