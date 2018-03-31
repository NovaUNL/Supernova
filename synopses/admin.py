from django.contrib import admin

from synopses.models import SynopsisArea, SynopsisSubarea, SynopsisTopic, SynopsisSection, ClassSynopsesSections, \
    SynopsisSectionTopic, SynopsisSectionLog

admin.site.register(SynopsisArea)
admin.site.register(SynopsisSubarea)
admin.site.register(SynopsisTopic)
admin.site.register(SynopsisSection)
admin.site.register(ClassSynopsesSections)
admin.site.register(SynopsisSectionTopic)
admin.site.register(SynopsisSectionLog)
