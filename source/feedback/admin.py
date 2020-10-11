from django.contrib import admin

from feedback import models as m

admin.site.register(m.Review)
admin.site.register(m.Suggestion)
admin.site.register(m.Report)