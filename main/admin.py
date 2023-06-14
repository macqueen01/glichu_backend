from django.contrib import admin
from .models import *


admin.site.register(User)
admin.site.register(Scrolls)
admin.site.register(VideoMedia)
admin.site.register(Cell)
admin.site.register(Tag)
admin.site.register(Remix)
admin.site.register(RemixPermission)
admin.site.register(DailyVisit)