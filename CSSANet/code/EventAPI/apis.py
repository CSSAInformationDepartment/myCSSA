import secrets

from django.db.models import F, Q
from django.db import transaction

from .models import *

def is_duplicated_purchase(user,event):
    '''
    Check if the user is going to proceed a duplicated purchase.
    '''
    current_ticket = AttendEvent.objects.filter(Q(attendedEventId=event) & Q(attendedUserId=user) & Q(disabled=False))
    if current_ticket:
        return True

    return False 

def check_availability(event):
    '''
    Check the availability of the event
    If yes, return the remaining sits
    If no, return False
    '''
    if event.hasMaxAttendent:
        event_max_attendent = event.maxAttendent
        current_attendent = AttendEvent.objects.filter(attendedEventId = event).count()
        if event_max_attendent > current_attendent:
            return (event_max_attendent - current_attendent)
        else:
            return False
    else:
        return True

def issue_token_for_ticket(ticket):
    '''
    Issue token for a ticket, which also make the ticket able to use
    '''

    _token = None
    
    while not _token:
        _token = secrets.token_urlsafe(256)
        check_duplicate_token = AttendEvent.objects.filter(token=_token).first()
        if check_duplicate_token:
            _token = None
        else:
            ticket.token = _token 
            ticket.save()
    
    return ticket


def get_ticket(user, event_id, ticket_id=None ,is_paid=False):
    '''
    Create Ticket for event attendent
    Will only give token when the event is free or fee is paid
    '''
    event = Event.objects.get(pk=event_id)

    if not is_duplicated_purchase(user, event):
        if ticket_id and is_paid:
            ticket = AttendEvent.objects.select_for_update().filter(attendedId=ticket_id).first()
            if ticket:
                ticket.paid = True
                return issue_token_for_ticket(ticket)
        elif check_availability(event):
            new_ticket = AttendEvent(
                attendedEventId = event,
                attendedUserId = user,
                paid = is_paid,
            )
            if event.isFree:
                return issue_token_for_ticket(new_ticket)
            else:
                return new_ticket.save()
    
    return False


def TicketsCheckIn(token):
    pass