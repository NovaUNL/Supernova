from django.contrib import admin
from learning import models as m
from learning import forms as f

# Register your models here.
class ClassSectionAdmin(admin.ModelAdmin):
    form = f.ClassSectionForm


class SectionInline(admin.TabularInline):
    model = m.SectionSubsection
    extra = 1
    fk_name = 'parent'


class SectionAdmin(admin.ModelAdmin):
    inlines = (SectionInline,)


admin.site.register(m.Area)
admin.site.register(m.Subarea)
admin.site.register(m.Section, SectionAdmin)
admin.site.register(m.SectionSubsection)
admin.site.register(m.ClassSection, ClassSectionAdmin)
admin.site.register(m.SectionLog)
admin.site.register(m.Exercise)