from django import forms

import models


class SyncAppModelForm(forms.ModelForm):

    class Meta:
        model = models.SyncAppModel
        exclude = ('last_sync_date', 'last_sync_status')


class SyncAppModelCopyForm(forms.Form):
    app_model = forms.CharField()
