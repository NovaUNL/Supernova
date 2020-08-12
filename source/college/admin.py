from college import models as m
from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin


class StudentClipStudentAdmin(admin.ModelAdmin):
    raw_id_fields = ("clip_student",)


admin.site.register(m.Building, LeafletGeoAdmin)
admin.site.register(m.Course)
admin.site.register(m.Curriculum)
admin.site.register(m.Class)
admin.site.register(m.ClassInstance)
admin.site.register(m.Room, LeafletGeoAdmin)
admin.site.register(m.Department)
admin.site.register(m.Enrollment)
admin.site.register(m.PlaceFeature)
admin.site.register(m.Place)
admin.site.register(m.Student)
admin.site.register(m.TurnStudents)
admin.site.register(m.Turn)
admin.site.register(m.TurnInstance)
