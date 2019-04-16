from django.test import TestCase, Client
from django.urls import reverse
from PublicSite import models, views
import json

'''
======================= Instructions of performing views unit tests =======================
1. set up a method named test_[views name]_[HTTP Method Name]

2. following the samples below to fill the internal code

3. 


Video Reference: https://www.youtube.com/watch?v=hA_VxnxCHbo
==========================================================================================
'''

class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        return super().setUp()

    def test_events_list_GET(self):
        response = self.client.get(reverse('PublicSite:events'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'PublicSite/event.html')

    def test_events_detail_GET(self):
        response = self.client.get(reverse('PublicSite:eventsDetails', args=[]))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'PublicSite/eventDetails.html')