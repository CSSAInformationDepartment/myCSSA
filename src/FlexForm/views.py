from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView
from EventAPI.models import *

from .forms import *
from .models import *


class FormListView(LoginRequiredMixin, ListView):
    '''
    Rendering the List of Flex Form Configuration
    '''
    login_url = '/hub/login/'
    template_name = 'FlexForm/form_list.html'
    model = FlexForm
    context_object_name = 'FormConfig'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for row in context[self.context_object_name]:
            print(row)
            setattr(row, 'field_count', FlexFormField.objects.filter(
                Q(form__id=row.id) & Q(disabled=False)).count())
            setattr(row, 'submission_count', FlexFormData.objects.filter(
                Q(field__form__id=row.id) & Q(field__disabled=False)).values('field__form', entries=Count('user')).count())

        return context


class CreateFormView(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'FlexForm/newform.html'
    form_class = NewFlexForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form': self.form_class})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(instance.get_absolute_url())

        return render(request, self.template_name, {'form': form})


class AddFormFieldView(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'FlexForm/form_field.html'
    form_class = AddFlexFormFieldForm

    def get_new_context(self, form=None, event_bind_form=None, *args, **kwargs):
        form_id = self.kwargs.get("formid")
        print(form_id)
        fields = FlexFormField.objects.filter(form__id=form_id)
        if not form:
            new_form = self.form_class(initial={'form': form_id})
        else:
            new_form = form

        if not event_bind_form:
            event_bind_form = AttachInfoCollectionForm(
                initial={'form': form_id})
        else:
            event_bind_form = event_bind_form

        bind_events = EventAttendentInfoForm.objects.filter(form__id=form_id)
        return {'form': new_form, 'FormConfig': fields, 'event_bind_form': event_bind_form, 'bind_events': bind_events}

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_new_context())

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST or None)
        event_bind = AttachInfoCollectionForm(request.POST or None)
        print(event_bind.errors)
        if form.is_valid() or event_bind.is_valid():
            if form.is_valid():
                form.save()
            if event_bind.is_valid():
                event_bind.save()
            return render(request, self.template_name, self.get_new_context())

        return render(request, self.template_name, self.get_new_context(form=form, event_bind_form=event_bind))
