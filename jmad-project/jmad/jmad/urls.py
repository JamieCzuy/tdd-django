from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin

import solos.views as solos_views


urlpatterns = [
    url(r'^$', solos_views.index),
    url(r'^admin/', include(admin.site.urls)),
]
