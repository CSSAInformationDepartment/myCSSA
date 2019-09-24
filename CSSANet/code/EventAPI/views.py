from django.shortcuts import render, get_object_or_404, Http404
from django.db.models import Q

from .models import *
from .forms import *
from .apis import is_duplicated_purchase

from myCSSAhub.apis import GetDocViewData
from UserAuthAPI.models import UserProfile, User
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.mixins import  LoginRequiredMixin, PermissionRequiredMixin
from django.utils.formats import localize
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from django.urls import reverse
from django.utils.html import escape
from pytz import timezone
from django.conf import settings
TIME_ZONE  = settings.TIME_ZONE

from CommunicateManager.send_email import send_emails
from FlexForm.apis import flexform_user_write_in
from EventAPI.apis import get_ticket,check_availability
from django.utils import timezone as sys_time

from PrizeAPI.apis import add_event_candidate_to_poll

# Create your views here.
class EventListView(LoginRequiredMixin, PermissionRequiredMixin, View):
    '''
    Provide a list of event that is currently registered in the system
    '''

    login_url = '/hub/login/'
    permission_required = ('EventAPI.add_event',)
    template_name = 'EventAPI/event_list.html'
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class EventStatView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    '''
    Provide the statistical data for event that has been open for enrolling
    '''

    login_url = '/hub/login/'
    permission_required = ('EventAPI.view_event',)
    template_name = 'EventAPI/event_stat.html'
    context_object_name = 'events'
    paginate_by = 15
    queryset = Event.objects.filter(disabled=False).order_by("-eventActualStTime")


class AttendantListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    '''
    List out all the attendants for a given event
    '''
    login_url = '/hub/login/'
    permission_required = ('EventAPI.view_event',)
    template_name = 'EventAPI/attendant_list.html'
    context_object_name = 'attendants'
    paginate_by = 15
    model = AttendEvent
    
    def get_queryset(self, *args, **kwargs):
        id = self.kwargs.get('id')
        qs = self.model.objects.filter(Q(attendedEventId__eventID=id) & Q(disabled=False))
        return qs


class AddEventView(LoginRequiredMixin, View):
    '''
    Adding a new event to the system
    '''
    login_url = '/hub/login/'
    template_name = 'EventAPI/add_event.html'
    form_class = AddEventForm
    
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'form':self.form_class,'submit_url':reverse('myCSSAhub:EventAPI:add_event')})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('myCSSAhub:EventAPI:event_list'))
        return render(request, self.template_name, {'form':form, 'submit_url':reverse('myCSSAhub:EventAPI:add_event')})


class UpdateEventView(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'EventAPI/add_event.html'
    form_class = AddEventForm
    
    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('id')
        obj = get_object_or_404(Event, eventID=id)
        form = self.form_class(instance=obj)
        return render(request, self.template_name, {'form':form, 'submit_url':reverse('myCSSAhub:EventAPI:update_event', args=[str(id)])})

    def post(self, request, *args, **kwargs):
        id = self.kwargs.get('id')
        obj = get_object_or_404(Event, eventID=id)
        form = self.form_class(data=request.POST or None, files=request.FILES or None, instance=obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('myCSSAhub:EventAPI:event_list'))
        return render(request, self.template_name, {'form':form, 'submit_url':reverse('myCSSAhub:EventAPI:update_event', args=[str(id)])})

class ConfirmEventOrderView(LoginRequiredMixin,View):
    login_url = '/hub/login/'
    template_name = 'EventAPI/confirm_order.html'
    
    def get_info_collection_form_field(self, *args, **kwargs):
        id = self.kwargs.get('id')
        info_collection_form = EventAttendentInfoForm.objects.filter(event__pk=id).first()
        if info_collection_form:
            info_form_field = FlexFormModel.FlexFormField.objects.filter(form__id=info_collection_form.form.id)
        else:
            info_form_field = None
        return info_form_field

    def get_context_data(self,user, *args, **kwargs):
        id = self.kwargs.get('id')
        event = get_object_or_404(Event, pk=id)
        now_time = sys_time.now()
        if is_duplicated_purchase(user,event):
            return {'event':event, 'now_time':now_time, 'duplicated_purchase':True}
        else:
            return {'event':event, 'info_form_field':self.get_info_collection_form_field(), 'now_time':now_time}

    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('id')
        event = get_object_or_404(Event, pk=id)
        now_time = sys_time.now()
        if event.eventSignUpTime > now_time:
            raise Http404("Event is not open for enrollment yet.")
        return render(request, self.template_name, self.get_context_data(user=request.user))  
    
    def post(self, request, *args, **kwargs):
        event_id = self.kwargs.get('id')
        user_profile = get_object_or_404(UserProfile, user__pk=request.user.id)
        fields = self.get_info_collection_form_field()

        if fields:
            field_data = {}
            for field in fields:
                field_data[field.id]=request.POST.get(str(field.id))
            flexform_user_write_in(user_profile, field_data)
       
        if get_ticket(request.user, event_id):
            return HttpResponseRedirect(reverse('myCSSAhub:EventAPI:user_ticket_list'))
        else:
            raise Http404("Ticket cannot be issued. Please contact the event manager")
        
        return render(request, self.template_name, self.get_context_data()) 

class EventCheckInSetupView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    '''
    The view to setup for attendant to check-in their tickets
    '''
    login_url = '/hub/login/'
    permission_required = ('EventAPI.view_event',)
    template_name ='EventAPI/event_checkin_setup.html'
    context_object_name ='events'
    model = Event 

    def get_queryset(self, *args, **kwargs):
        melb_date=sys_time.localdate(sys_time.now())
        
        print(melb_date)
        qs = self.model.objects.filter(Q(eventActualStTime__date=melb_date) & Q(disabled=False))
        return qs

class TicketCheckInView(LoginRequiredMixin, PermissionRequiredMixin, View):
    '''
    The view to setup for attendant to check-in their tickets
    '''
    login_url = '/hub/login/'
    permission_required = ('EventAPI.view_event',)
    template_name ='EventAPI/ticket_check_in.html'
    model = AttendEvent 

    def get(self, request, *args, **kwargs):
        event_id = self.kwargs.get('event_id')
        melb_date=sys_time.localdate(sys_time.now())
        
        return render(request, self.template_name)

    def post(self, request, *args, **kwagrs):
        event_id = self.kwargs.get('event_id')
        manual_check_input = request.POST.get('identity-check')
        qr_code = request.POST.get('qr-decoded')

        if manual_check_input:
            user = UserProfile.objects.filter(Q(studentId=manual_check_input)
                | Q(membershipId=manual_check_input)
                | Q(user__telNumber=manual_check_input)).first()
            if user:
                ticket = AttendEvent.objects.filter(Q(attendedEventId__pk=event_id) 
                    & Q(attendedUserId=user) & Q(token_used=False)).first()
                print(ticket)
                if ticket:
                    ticket.token_used=True
                    ticket.save()
                    add_event_candidate_to_poll(user,ticket.attendedEventId, 
                        ticket.attendedEventId.eventActualStTime)
                    return JsonResponse(
                        {'success': True,
                        'type':0,
                        'message':"Check-in Successful"}
                    )
            return JsonResponse(
                        {'success': False,
                        'type':1,
                        'message':"No valid ticket for this event"}
                    )
        return JsonResponse(
                        {'success': False,
                        'type':0,
                        'message':"Empty Request"}
                    )

class UserTicketListView(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'EventAPI/user_ticket_list.html'

    def get(self, request, *args, **kwargs):
        tickets = AttendEvent.objects.filter(attendedUserId__user=request.user).order_by("-attendedEventId__eventActualStTime")
        return render(request, self.template_name, {'tickets':tickets})

class EventListJsonView(LoginRequiredMixin, PermissionRequiredMixin, BaseDatatableView):
    login_url = '/hub/login/'
    permission_required = ('EventAPI.add_event',)
    model = Event

    # define the columns that will be returned
    columns = ['eventID', 'eventName','eventSignUpTime', 'eventActualStTime','venue']
    order_columns = columns

    max_display_length = 500

    def render_column(self, row, column):
        # Customer HTML column rendering
        if (column == 'eventSignUpTime'):
            return row.eventSignUpTime.strftime('%Y-%m-%d %H:%M')
        elif (column == 'eventActualStTime'):
            return row.eventActualStTime.strftime('%Y-%m-%d %H:%M')
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

########Start###################### Event API for mobile App ##################Start###################
from rest_framework.views import APIView
from .serializers import EventsSerializer
import base64, json
from django.core.serializers.json import DjangoJSONEncoder
# from rest_framework.response import Response
# from django.core import serializers

class MobilePastEventAPI(APIView):
    def get(self, request, format=None):
        sys_time.activate('Australia/Melbourne')
        now_time = sys_time.now()
        eventsPast= Event.objects.filter(eventActualStTime__lt=now_time).order_by("eventActualStTime")    
        
        # queryset是实例集合，需要加 many=True ，如果是单个实例，可以不用加 many=True
        serializer = EventsSerializer(eventsPast, many = True)
        
        # data = serializers.serialize("json",serializer.eventsPast) # 直接序列化成json形式

        # 两种返回方法都行，下面一种需要设置，设定已标注
        # In order to allow non-dict objects to be serialized set the safe parameter to False
        data = json.dumps(serializer.data, cls=DjangoJSONEncoder)
        # 这里需要加encode()才能通过base64进行编码
        data_encode = base64.b64encode(data.encode())
        # return JsonResponse(serializer.data, safe=False)
        return HttpResponse(data_encode, content_type="text/plain")


class MobileFutureEventAPI(APIView):
    #原理同上   
    def get(self, request, format=None):
        sys_time.activate('Australia/Melbourne')
        now_time = sys_time.now()
        eventsFuture = Event.objects.filter(eventActualStTime__gt=now_time).order_by("eventActualStTime")
        serializer = EventsSerializer(eventsFuture, many = True)
        data = json.dumps(serializer.data, cls=DjangoJSONEncoder)
        data_encode = base64.b64encode(data.encode())
        return HttpResponse(data_encode, content_type="text/plain")


########End######################## Event API for mobile App ######################End##############