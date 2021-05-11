from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import json

# Create your views here.

from django.shortcuts import render, get_object_or_404, redirect

from myCSSAhub import models as HubModels

# Reference: https://gist.github.com/leemac/bf0cef7ad214cfc950dd

def Merchants(request):
    merchants = HubModels.DiscountMerchant.objects.filter(merchant_type='折扣商家')
    jsonRes = []
    for merchant in merchants:
        jsonObj = dict(name=merchant.merchant_name, sale=merchant.merchant_description, \
                       location=merchant.merchant_address, img=str(merchant.merchant_image.url))
        jsonRes.append(jsonObj)
    return HttpResponse(json.dumps(jsonRes), content_type='application/json')


def Sponsors(request):
    merchants = HubModels.DiscountMerchant.objects.filter(merchant_type='赞助商家')
    jsonRes = []
    for merchant in merchants:
        jsonObj = dict(name=merchant.merchant_name, details=merchant.merchant_description, \
                       priority=merchant.merchant_level, img=str(merchant.merchant_image.url))
        jsonRes.append(jsonObj)
    return HttpResponse(json.dumps(jsonRes), content_type='application/json')