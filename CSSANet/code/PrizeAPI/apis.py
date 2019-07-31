from . import models
from django.db.models import Q


def add_member_to_poll(user,tag):
    '''
    Provide a unbinded pool for lucky draw candidates
    '''
    seed = models.PrizePool(
        user = user,
        group_tag = tag)

    seed.save()

    return seed

def add_event_candidate_to_poll(user,event,tag):
    '''
    Provide a event-binded pool for lucky draw candidates,
    tag should be eventActualStTime
    '''
    instance = add_member_to_poll(user,tag)
    instance.event_related = event

    instance.save()

    return instance


def get_pool_by_group_tag(tag):
    return models.PrizePool.objects.filter(group_tag = tag)

def get_pool_by_event(event,tag):
    return models.PrizePool.objects.filter(Q(group_tag = tag)
        & Q(event_related=event))