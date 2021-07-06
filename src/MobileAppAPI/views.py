from django.http import HttpResponse, HttpResponseForbidden
import json

from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

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

# Specify the POST request, and authenticated user
@api_view(['POST'])
@permission_classes([IsAuthenticated])
# This function is to update merchant/sponsor's information
def UpdateMerchants(request):
    user = request.user
    # Check permission
    if user.has_perm('can_change_discount_merchants'):
        have_update = False
        request_data = json.loads(request.body)
        profileID = request_data.get('id')
        # Get the record to update
        obj = get_object_or_404(DiscountMerchant, merchant_id=profileID)
        form = MerchantsForm(data=request_data or None,
                               files=request.FILES or None,
                               instance=obj)
        # Validate form, and save the update
        if form.is_valid():
            form.save()
            have_update = True
        return HttpResponse(json.dumps({'update': have_update}), content_type='application/json')
    else:
        return HttpResponseForbidden("No permission")

# Similar to previous one, but without getting existed record
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def AddMerchants(request):
    user = request.user
    if user.has_perm('can_add_discount_merchants'):
        have_update = False
        request_data = json.loads(request.body)
        form = MerchantsForm(data=request_data or None,
                               files=request.FILES or None)
        if form.is_valid():
            form.save()
            have_update = True
        return HttpResponse(json.dumps({'update': have_update}), content_type='application/json')
    else:
        return HttpResponseForbidden("No permission")