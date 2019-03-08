from django.contrib import admin

from synopses.forms import ClassSectionForm
from synopses.models import Area, Subarea, Topic, Section, ClassSection, SectionTopic, SectionLog


class ClassSectionAdmin(admin.ModelAdmin):
    form = ClassSectionForm


admin.site.register(Area)
admin.site.register(Subarea)
admin.site.register(Topic)
admin.site.register(Section)
admin.site.register(ClassSection, ClassSectionAdmin)
admin.site.register(SectionTopic)
admin.site.register(SectionLog)
