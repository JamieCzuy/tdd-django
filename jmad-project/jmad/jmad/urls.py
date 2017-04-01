from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin

import solos.views as solos_views
from solos.views import SoloDetailView


urlpatterns = [
    url(r'^$', solos_views.index),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^recordings/(?P<album>[\w-]+)/(?P<track>[\w-]+)/(?P<artist>[\w-]+)/$',
        SoloDetailView.as_view()),
]
