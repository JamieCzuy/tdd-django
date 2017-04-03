from django.core.urlresolvers import reverse
from django.db import models

from albums.models import Track


class Solo(models.Model):
    track = models.ForeignKey(Track)
    artist = models.CharField(max_length=100)
    instrument = models.CharField(max_length=50)
    start_time = models.CharField(max_length=20, blank=True, null=True)
    end_time = models.CharField(max_length=20, blank=True, null=True)
    slug = models.SlugField()

    def get_absolute_url(self):
        return reverse('solo_detail_view', kwargs={
            'album': self.track.album.slug,
            'track': self.track.slug,
            'artist': self.slug,
        })

    def get_duration(self):
        if self.start_time and self.end_time:
            return '{}-{}'.format(self.start_time, self.end_time)
        else:
            return ''

    class Meta:
        ordering = ['track', 'start_time']
