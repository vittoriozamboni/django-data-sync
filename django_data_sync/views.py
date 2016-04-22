import unicodecsv as csv
import json

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from braces.views import LoginRequiredMixin, JSONResponseMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
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


class SyncAppModelListView(LoginRequiredMixin, SyncAppModelMixin, ListView):
    template_name = 'django_data_sync%s/sync_app_model_list.html' % TS

    def get_queryset(self):
        return models.SyncAppModel.objects.all()


class SyncAppModelDetailView(LoginRequiredMixin, SyncAppModelMixin, DetailView):
    template_name = 'django_data_sync%s/sync_app_model_detail.html' % TS


class SyncAppModelCreateView(LoginRequiredMixin, SyncAppModelMixin, CreateView):
    template_name = 'django_data_sync%s/sync_app_model_form.html' % TS


class SyncAppModelEditView(LoginRequiredMixin, SyncAppModelMixin, UpdateView):
    template_name = 'django_data_sync%s/sync_app_model_form.html' % TS


class SyncAppModelDeleteView(LoginRequiredMixin, SyncAppModelMixin, DeleteView):
    template_name = 'django_data_sync%s/sync_app_model_confirm_delete.html' % TS

    def get_success_url(self):
        return reverse('django_data_sync:sync_app_model_list')


class SyncAppModelCopyView(LoginRequiredMixin, SyncAppModelMixin, FormView):
    template_name = 'django_data_sync%s/sync_app_model_confirm_copy.html' % TS
    form_class = forms.SyncAppModelCopyForm

    def get_context_data(self, **kwargs):
        context = super(SyncAppModelCopyView, self).get_context_data(**kwargs)
        context['sync_app_model'] = models.SyncAppModel.objects.get(id=self.kwargs['pk'])
        return context

    def get_initial(self):
        initial = super(SyncAppModelCopyView, self).get_initial()
        initial['app_model'] = models.SyncAppModel.objects.get(id=self.kwargs['pk']).app_model
        return initial

    def form_valid(self, form):
        sync_app_model = models.SyncAppModel.objects.get(id=self.kwargs['pk'])
        sync_app_model.pk = None
        sync_app_model.id = None
        sync_app_model.app_model = form.cleaned_data['app_model']
        sync_app_model.save()
        return HttpResponseRedirect(sync_app_model.get_absolute_url())


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
