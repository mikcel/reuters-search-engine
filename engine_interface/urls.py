from django.conf.urls import url

from engine_interface.views import *

urlpatterns = [
    url(r'^$', index, name='index'),
    url(r'^search_query', search_index, name='search_index')
]
