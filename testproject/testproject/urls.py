from django.conf.urls import include, url
from django.contrib import admin

from testproject import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.TestView.as_view(), name='home'),
    url(r'^groups-manager/', include('django_data_sync.urls', namespace='django_data_sync')),
]
