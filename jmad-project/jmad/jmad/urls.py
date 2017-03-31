from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin

import solos


urlpatterns = [
    url(r'^$', solos.views.index),
    url(r'^admin/', include(admin.site.urls)),
]
