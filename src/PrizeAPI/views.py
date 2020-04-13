from django.shortcuts import render
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.views import View
from django.views.generic import CreateView, UpdateView, FormView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin

from EventAPI.models import Event
from PrizeAPI.models import *
from PrizeAPI.apis import (get_pool_by_event, get_pool_by_group_tag)

from typing import Any
# Create your views here.

################################# lucky draw ########################################

class LuckyDrawEventView(LoginRequiredMixin, ListView):
    login_url = '/hub/login/'
    template_name = 'PrizeAPI/event_luckyDraw.html'
    context_object_name ='events'
    paginate_by = 15
    queryset = Event.objects.filter(disabled=False).order_by("-eventActualStTime")

class LuckyDrawView(LoginRequiredMixin, View):
    login_url = 'hub/login/'
    template_name = 'myCSSAhub/luckyDraw.html'

    def get(self, request, *args, **kwargs):
        event_id = self.kwargs.get('id')
        print(event_id)
        return render(request, self.template_name, {'event_id':event_id})


class LuckyDrawDataView(LoginRequiredMixin, View):
    login_url = 'hub/login/'
    ViewBag:Any ={}

    def get(self, request, *args, **kwargs):
        event_id = self.kwargs.get('id')
        if event_id is not None:
            try:
                event_instance = Event.objects.get(eventID = event_id)
            except:
                return HttpResponseBadRequest("Event ID is not Valid") 
        lucky_list=[]
        candidates = get_pool_by_event(event_instance, event_instance.eventActualStTime)
        for member in candidates:
            lucky_list.append(member.user.studentId)
        self.ViewBag['new_student_id']=lucky_list
        return JsonResponse(self.ViewBag)
