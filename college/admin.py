from django.contrib import admin

from college.models import Student, Auditorium, Laboratory, Classroom, BuildingUsage, Department, Place, Building, \
    Course, CourseArea, Area, Curriculum, TurnStudents, Class, Turn, Enrollment, TurnInstance, ClassInstance


class StudentClipStudentAdmin(admin.ModelAdmin):
    raw_id_fields = ("clip_student",)


admin.site.register(Area)
admin.site.register(Auditorium)
admin.site.register(Building)
admin.site.register(BuildingUsage)
admin.site.register(Course)
admin.site.register(CourseArea)
admin.site.register(Curriculum)
admin.site.register(Class)
admin.site.register(ClassInstance)
admin.site.register(Classroom)
admin.site.register(Department)
admin.site.register(Enrollment)
admin.site.register(Laboratory)
admin.site.register(Place)
admin.site.register(Student)
admin.site.register(TurnStudents)
admin.site.register(Turn)
admin.site.register(TurnInstance)
