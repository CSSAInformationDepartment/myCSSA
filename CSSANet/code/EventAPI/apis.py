import secrets
from .forms import *

def GetTickets(user_id, event_id, is_paid=False):
    '''
    Create Ticket for event attendent
    '''
    if user and event:
        ticket = AttendEventForm
        ticket.attendedEventId = event_id
        ticket.attendUserId = user_id
        _token = None
        while not _token:
            _token = secrets.token_urlsafe(256)


def TicketsCheckIn(token):
    pass