from django.urls import path

from .views import *

app_name = "FlexForm"
urlpatterns = [
    path('list/', FormListView.as_view(), name="formlist"),
    path('newform/', CreateFormView.as_view(), name="create_new_form"),
    path('addfield/<str:formid>', AddFormFieldView.as_view(), name="add_form_field"),

]
