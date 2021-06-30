from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from django.http import JsonResponse
import json

# Create your views here.

from django.shortcuts import render, get_object_or_404, redirect
from django.db import models

from myCSSAhub.models import *
from myCSSAhub.forms import MerchantsForm

# Reference: https://gist.github.com/leemac/bf0cef7ad214cfc950dd

def Merchants(request):
    user = request.user
    if user.has_perm('can_change_discount_merchants'):
        print('Yes')
    else:
        print('No')


    merchants = HubModels.DiscountMerchant.objects.filter(merchant_type='折扣商家')
    jsonRes = []
    for merchant in merchants:
        jsonObj = dict(id=merchant.merchant_id, name=merchant.merchant_name, sale=merchant.merchant_description, \
                       location=merchant.merchant_address, img=str(merchant.merchant_image.url))
        jsonRes.append(jsonObj)
    return HttpResponse(json.dumps(jsonRes), content_type='application/json')


def Sponsors(request):
    merchants = HubModels.DiscountMerchant.objects.filter(merchant_type='赞助商家')
    jsonRes = []
    for merchant in merchants:
        jsonObj = dict(id=merchant.merchant_id, name=merchant.merchant_name, details=merchant.merchant_description, \
                       priority=merchant.merchant_level, img=str(merchant.merchant_image.url))
        jsonRes.append(jsonObj)
    return HttpResponse(json.dumps(jsonRes), content_type='application/json')

# 为了保证网站的安全，我们开启了CSRF验证，这要求在发送POST请求时要带上CSRF值
# 需要带CSRF的有三个地方：
# 1. Post Form里有一个 {"csrfmiddlewaretoken": $CSRF_TOKEN$}
# 2. Request的Header里有一个 {"X-CSRFToken": $CSRF_TOKEN$}
# 3. Request的Header里有一个{"Cookie": "csrftokenk=$CSRF_TOKEN$;sessionid=%SESSION_ID%"}

def UpdateMerchants(request):
    if request.method == 'POST':
        user = request.user
        # check permission

        if user.has_perm('can_change_discount_merchants'):
            have_update = False
            data = request.POST
            profileID = data.get('id')
            obj = get_object_or_404(DiscountMerchant, merchant_id=profileID)
            # return HttpResponse(json.dumps(obj.merchant_name), content_type='application/json')

            form = MerchantsForm(data=request.POST or None,
                                   files=request.FILES or None,
                                   instance=obj)
            if form.is_valid():
                form.save()
                have_update = True

            return HttpResponse(json.dumps({'update': have_update}), content_type='application/json')

        else:
            return HttpResponseForbidden("No permission")

# def UpdateSponsors(request):
    #