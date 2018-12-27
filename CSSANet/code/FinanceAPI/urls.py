
from django.urls import path, re_path, include
from FinanceAPI import views


app_name = "FinanceAPI"
urlpatterns = [
    path('list/',views.TransactionListView.as_view(),name="transaction_list"),
    path('create/',views.CreateTransactionView.as_view(),name="transaction_create"),
    path('<str:id>/',views.TransactionDetailView.as_view(),name="transaction_details"),

]


## Internal AJAX path
urlpatterns += [

]