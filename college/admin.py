from college.models import Student, Room, Department, Place, Building, \
    Course, CourseArea, Area, Curriculum, TurnStudents, Class, Turn, Enrollment, TurnInstance, ClassInstance, Feature
from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin


class StudentClipStudentAdmin(admin.ModelAdmin):
    raw_id_fields = ("clip_student",)


admin.site.register(Area)
admin.site.register(Building, LeafletGeoAdmin)
admin.site.register(Course)
admin.site.register(CourseArea)
admin.site.register(Curriculum)
admin.site.register(Class)
admin.site.register(ClassInstance)
admin.site.register(Room, LeafletGeoAdmin)
admin.site.register(Department)
admin.site.register(Enrollment)
admin.site.register(Feature)
admin.site.register(Place)
admin.site.register(Student)
admin.site.register(TurnStudents)
admin.site.register(Turn)
admin.site.register(TurnInstance)
