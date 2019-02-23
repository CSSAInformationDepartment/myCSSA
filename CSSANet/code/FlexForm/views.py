from django.shortcuts import render

from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count

from .models import *
from .forms import *
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.mixins import  LoginRequiredMixin, PermissionRequiredMixin
from django.utils.formats import localize
from django.views import View
from django.views.generic import ListView, DetailView, FormView
from django.urls import reverse
from django.utils.html import escape

class FormListView(LoginRequiredMixin,ListView):
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
                Q(form__id=row.id)&Q(disabled=False)).count())
            setattr(row, 'submission_count', FlexFormData.objects.filter(
                Q(field__form__id=row.id)&Q(field__disabled=False)).values('field__form', entries=Count('user')).count())
        
        return context


class CreateFormView(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'FlexForm/newform.html'
    form_class = NewFlexForm

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form':self.form_class})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(instance.get_absolute_url())

        return render(request, self.template_name, {'form':form})


class AddFormFieldView(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'FlexForm/form_field.html'
    form_class = AddFlexFormFieldForm

    def get(self, request, *args, **kwargs):
        form_id = self.kwargs.get("formid")
        fields = FlexFormField.objects.filter(form__id=form_id)
        new_form = self.form_class(initial={'form':form_id})
        return render(request, self.template_name, {'form':new_form, 'FormConfig':fields})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        form_id = self.kwargs.get("formid")
        fields = FlexFormField.objects.filter(form__id=form_id)
        if form.is_valid():
            form.save()
            new_form = self.form_class
            new_form = self.form_class(initial={'form':form_id})
            return render(request, self.template_name, {'form':new_form, 'FormConfig':fields})
        
        return render(request, self.template_name, {'form':form, 'FormConfig':fields})