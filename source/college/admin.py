from django.contrib import admin

from leaflet.admin import LeafletGeoAdmin

from college import models as m
from college import forms as f


class CurriculumClassComponentAdmin(admin.ModelAdmin):
    form = f.CurriculumClassComponentForm


class CurriculumBlockComponentAdmin(admin.ModelAdmin):
    form = f.CurriculumBlockComponentForm


class CurriculumBlockVariantComponentAdmin(admin.ModelAdmin):
    form = f.CurriculumBlockVariantComponentForm


admin.site.register(m.Building, LeafletGeoAdmin)
admin.site.register(m.Course)
admin.site.register(m.CurricularClassComponent, CurriculumClassComponentAdmin)
admin.site.register(m.CurricularBlockComponent, CurriculumBlockComponentAdmin)
admin.site.register(m.CurricularBlockVariantComponent, CurriculumBlockVariantComponentAdmin)
admin.site.register(m.Curriculum)
admin.site.register(m.Class)
admin.site.register(m.ClassInstance)
admin.site.register(m.Room, LeafletGeoAdmin)
admin.site.register(m.Department)
admin.site.register(m.Enrollment)
admin.site.register(m.PlaceFeature)
admin.site.register(m.Place)
admin.site.register(m.Student)
admin.site.register(m.ShiftStudents)
admin.site.register(m.Shift)
admin.site.register(m.ShiftInstance)
admin.site.register(m.Teacher)
admin.site.register(m.TeacherRank)
