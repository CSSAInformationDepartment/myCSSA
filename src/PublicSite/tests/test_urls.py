from django.test import SimpleTestCase
from django.urls import resolve, reverse

from .. import views

'''
======================= Instructions of performing urls unit tests =======================
1. set up a method named test_[url path name]_resolved

2. following the samples below to fill the internal code

3. if the target view is a class-based view, change:
    resolve(url).func  >>> resolve(url).func.view_class


Video Reference: https://www.youtube.com/watch?v=0MrgsYswT1c
==========================================================================================

'''


class TestUrls(SimpleTestCase):

    def test_index_url_resolved(self):
        '''
        Testing root url of public site
        '''

        url = reverse('PublicSite:index')
        self.assertEqual(resolve(url).func, views.index)

    def test_contact_url_resolved(self):
        '''
        Testing url of contact detail page >> contact/
        '''

        url = reverse('PublicSite:contact')
        self.assertEqual(resolve(url).func, views.ContactUs)

    def test_events_url_resolved(self):
        '''
        Testing url of event page >> events/
        '''

        url = reverse('PublicSite:events')
        self.assertEqual(resolve(url).func.view_class, views.EventsListView)
