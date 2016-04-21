import unicodecsv as csv
import json

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from braces.views import LoginRequiredMixin, JSONResponseMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateView, View

from django_data_sync import models, settings, forms

TS = settings.DJANGO_DATA_SYNC['TEMPLATE_STYLE']


class DjangoDataSyncView(TemplateView):
    template_name = 'django_data_sync%s/django_data_sync_home.html' % TS


'''
SyncAppModel
'''


class SyncAppModelMixin(object):
    context_object_name = 'sync_app_model'
    model = models.SyncAppModel
    form_class = forms.SyncAppModelForm

    def get_success_url(self):
        sync_app_model = self.object
        return sync_app_model.get_absolute_url()


class OrganizationsView(LoginRequiredMixin, TemplateView):
    template_name = 'django_data_sync%s/sync_app_models.html' % TS


class SyncAppModelListView(LoginRequiredMixin,
                                        SyncAppModelMixin, ListView):
    template_name = 'django_data_sync%s/sync_app_model_list.html' % TS

    def get_queryset(self):
        return models.SyncAppModel.objects.all()


class SyncAppModelDetailView(LoginRequiredMixin,
                                          SyncAppModelMixin, DetailView):
    template_name = 'django_data_sync%s/sync_app_model_detail.html' % TS


class SyncAppModelCreateView(LoginRequiredMixin,
                                          SyncAppModelMixin, CreateView):
    template_name = 'django_data_sync%s/sync_app_model_form.html' % TS


class SyncAppModelEditView(LoginRequiredMixin,
                                        SyncAppModelMixin, UpdateView):
    template_name = 'django_data_sync%s/sync_app_model_form.html' % TS


class SyncAppModelDeleteView(LoginRequiredMixin,
                                          SyncAppModelMixin, DeleteView):
    template_name = 'django_data_sync%s/sync_app_model_confirm_delete.html' % TS

    def get_success_url(self):
        return reverse('django_data_sync:sync_app_model_list')


class SyncAppModelSyncView(LoginRequiredMixin, JSONResponseMixin, TemplateView):
    template_name = 'django_data_sync%s/sync_app_model_sync.html' % TS

    def get_context_data(self, **kwargs):
        context = super(SyncAppModelSyncView, self).get_context_data(**kwargs)
        #context['form'] = forms.SyncAppModelSyncForm()
        return context

    def post(self, request, *args, **kwargs):
        context = super(SyncAppModelSyncView, self).get_context_data(**kwargs)
        '''
        form = forms.SyncAppModelSyncForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect(
                reverse('django_data_sync:sync_app_models_sync_app_model_list'))
        context['form'] = form
        '''
        return self.render_to_response(context)
