from django.contrib import admin

from .models import Album
from .models import Track


class TrackAdmin(admin.ModelAdmin):
    model = Track
    list_display = ('album', 'name', 'track_number')

admin.site.register(Album)
admin.site.register(Track, TrackAdmin)
