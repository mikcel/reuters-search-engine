from django.conf.urls import url

from engine_interface.views import index

urlpatterns = [
    url(r'^$', index, name='index'),
]
