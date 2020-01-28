from django.contrib import admin

from synopses.forms import ClassSectionForm
from synopses.models import Area, Subarea, Topic, Section, ClassSection, SectionTopic, SectionLog, SectionSubsection


class ClassSectionAdmin(admin.ModelAdmin):
    form = ClassSectionForm



class SectionInline(admin.TabularInline):
    model = SectionSubsection
    extra = 1
    fk_name = 'parent'


class SectionAdmin(admin.ModelAdmin):
    inlines = (SectionInline,)

admin.site.register(Area)
admin.site.register(Subarea)
admin.site.register(Topic)
admin.site.register(Section, SectionAdmin)
admin.site.register(SectionSubsection)
admin.site.register(ClassSection, ClassSectionAdmin)
admin.site.register(SectionTopic)
admin.site.register(SectionLog)
