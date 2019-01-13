from django import forms


class NotificationForm(forms.Form):

    recID = forms.CharField(label="接受者ID", max_length=50)
    content = forms.CharField(label="站内信内容", max_length=200)
    title = forms.CharField(label="站内信标题", max_length=200)


class MerchantsForm(forms.Form):

    image = forms.ImageField()
    name = forms.CharField(label="商家名", max_length=256)
    address = forms.CharField(label="商家地址", max_length=256)
    description = forms.CharField(label="商家介绍", max_length=256)
    phone = forms.CharField(label="联系电话", max_length=256)
    link = forms.CharField(label="商家网站", max_length=256)
