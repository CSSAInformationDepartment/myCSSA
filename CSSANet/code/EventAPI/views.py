from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .models import *
from .forms import *

from myCSSAhub.apis import GetDocViewData
from UserAuthAPI.models import UserProfile
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.mixins import  LoginRequiredMixin, PermissionRequiredMixin
from django.utils.formats import localize
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from django.urls import reverse
from django.utils.html import escape
from pytz import timezone
from CSSANet.settings import TIME_ZONE

from myCSSAhub.send_email import send_emails


# Create your views here.
class EventListView(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'EventAPI/event_list.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class AddEventView(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'EventAPI/add_event.html'
    form_class = AddEventForm
    
    def get(self, request, *args, **kwargs):
        print(self.form_class)
        return render(request, self.template_name, {'form':self.form_class})

    def post(self, request, *args, **kwargs):
        form = AddEventForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('myCSSAhub:EventAPI:event_list'))
        print(form.errors)
        return render(request, self.template_name, {'form':form})



class EventListJsonView(LoginRequiredMixin, PermissionRequiredMixin, BaseDatatableView):
    login_url = '/hub/login/'
    permission_required = ('EventAPI.view_event',)
    model = Event

    # define the columns that will be returned
    columns = ['eventID', 'eventName','eventSignUpTime', 'eventActualStTime','venue']
    order_columns = columns

    max_display_length = 500

    def render_column(self, row, column):
        # Customer HTML column rendering
        if (column == 'eventSignUpTime'):
            return localize(row.eventSignUpTime)
        elif (column == 'eventActualStTime'):
            return localize(row.eventActualStTime)
        else:
            return super(EventListJsonView, self).render_column(row, column)

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.filter(disabled=False).order_by('-eventStartTime')

    def filter_queryset(self, qs):
        # DO NOT CHANGE THIS LINE
        search = self.request.GET.get('search[value]', None)

        if search:
            qs = qs.filter(Q(eventName__istartswith=search))
        return qs