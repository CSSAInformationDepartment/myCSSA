from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .models import *
from .forms import *
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.mixins import  LoginRequiredMixin, PermissionRequiredMixin
from django.utils.formats import localize
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from django.urls import reverse
from django.utils.html import escape

class FormListView(LoginRequiredMixin,ListView):
    login_url = '/hub/login/'
    template_name = 'EventAPI/event_list.html'
    model = FlexForm

