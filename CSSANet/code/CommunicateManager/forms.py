from django import forms
class NotificationForm(forms.Form):

    recID = forms.CharField(label="接受者ID", max_length=50)
    content = forms.CharField(label="站内信内容", max_length=200)
    title = forms.CharField(label="站内信标题", max_length=200)


