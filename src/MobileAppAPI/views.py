from django.http import HttpResponse, HttpResponseForbidden
import json

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser, JSONParser

from myCSSAhub.models import *
from myCSSAhub.forms import MerchantsForm

# Reference: https://gist.github.com/leemac/bf0cef7ad214cfc950dd

# This function is used for getting all merchants
def Merchants(request):
    # Filter function is like "WHERE" in SQL to filter data
    merchants = DiscountMerchant.objects.filter(merchant_type='折扣商家')
    jsonRes = []
    for merchant in merchants:
        jsonObj = dict(id=merchant.merchant_id, name=merchant.merchant_name, sale=merchant.merchant_description, \
                       location=merchant.merchant_address, img=str(merchant.merchant_image.url))
        jsonRes.append(jsonObj)
    return HttpResponse(json.dumps(jsonRes), content_type='application/json')

# This function is used for getting all sponsors
def Sponsors(request):
    merchants = DiscountMerchant.objects.filter(merchant_type='赞助商家')
    jsonRes = []
    for merchant in merchants:
        jsonObj = dict(id=merchant.merchant_id, sponsor=merchant.merchant_name, details=merchant.merchant_description, \
                       priority=merchant.merchant_level, logo=str(merchant.merchant_image.url), join_date=merchant.merchant_add_date.strftime("%Y-%m-%d"), \
                       location=merchant.merchant_address, website=merchant.merchant_link)
        jsonRes.append(jsonObj)
    return HttpResponse(json.dumps(jsonRes), content_type='application/json')

# api_view documentation:
# https://www.django-rest-framework.org/api-guide/views/
# Specify the POST request, and authenticated user
@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
# This function is to update merchant/sponsor's information
def UpdateMerchants(request):
    user = request.user
    # Check permission
    if user.has_perm('can_change_discount_merchants'):
        if request.method == "POST":

            have_update = False
            request_data = request.POST
            profileID = request_data.get('id')

            # Get the record to update
            obj = get_object_or_404(DiscountMerchant, merchant_id=profileID)
            form = MerchantsForm(data=request.POST or None,
                                   files=request.FILES or None,
                                   instance=obj)
            # Validate form, and save the update
            if form.is_valid():
                form.save()
                have_update = True
            else:
                print(form.errors)
            return HttpResponse(json.dumps({'update': have_update}), content_type='application/json')

        elif request.method == "GET":
            print(request.GET)
            profileID = request.GET.get('id')
            # Get the record to update
            merchant = get_object_or_404(DiscountMerchant, merchant_id=profileID)
            jsonObj = dict(id=merchant.merchant_id,
                           sponsor=merchant.merchant_name,
                           details=merchant.merchant_description, \
                           priority=merchant.merchant_level,
                           logo=str(merchant.merchant_image.url),
                           join_date=merchant.merchant_add_date.strftime(
                               "%Y-%m-%d"), \
                           location=merchant.merchant_address,
                           website=merchant.merchant_link)
            return HttpResponse(json.dumps(jsonObj), content_type='application/json')
    else:
        return HttpResponseForbidden("No permission")

# Similar to previous one, but without getting existed record
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def AddMerchants(request):
    user = request.user
    print(request.POST)
    if user.has_perm('can_add_discount_merchants'):
        have_update = False
        form = MerchantsForm(data=request.POST or None,
                               files=request.FILES or None)
        if form.is_valid():
            form.save()
            have_update = True
        else:
            print(form.errors)
        return HttpResponse(json.dumps({'update': have_update}), content_type='application/json')
    else:
        return HttpResponseForbidden("No permission")