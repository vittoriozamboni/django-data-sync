from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',

    url(r'^$',
        views.DjangoDataSyncView.as_view(),
        name='django_data_sync',),

    url(r'^sync-app-model/$',
        views.SyncAppModelListView.as_view(),
        name='sync_app_model_list',),
    url(r'^sync-app-model/(?P<pk>\d+)/$',
        views.SyncAppModelDetailView.as_view(),
        name='sync_app_model_detail',),
    url(r'^sync-app-model/(?P<pk>\d+)/edit/$',
        views.SyncAppModelEditView.as_view(),
        name='sync_app_model_edit',),
    url(r'^sync-app-model/add/$',
        views.SyncAppModelCreateView.as_view(),
        name='sync_app_model_add',),
    url(r'^sync-app-model/(?P<pk>\d+)/delete/$',
        views.SyncAppModelDeleteView.as_view(),
        name='sync_app_model_delete',),
    url(r'^sync-app-model/(?P<pk>\d+)/copy/$',
        views.SyncAppModelCopyView.as_view(),
        name='sync_app_model_copy',),
    url(r'^sync-app-model/sync/$',
        views.SyncAppModelSyncView.as_view(),
        name='sync_app_model_sync',),

)
