from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import  LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape

from FinanceAPI import models, forms


class TransactionListView(LoginRequiredMixin, View):
    login_url = 'hub/login/'
    template_name = 'FinanceAPI/transaction_list.html'
    
    #请求处理函数 （get）
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class TransactionListJson(LoginRequiredMixin, BaseDatatableView):
    login_url = 'hub/login/'
    model = models.Transaction

    # define the columns that will be returned
    columns = ['id', 'time','transaction_type', 'related_user', 'is_expense', 'amount','is_effective']
    
    # define column names that will be used in sorting
    # order is important and should be same as order of columns
    # displayed by datatables. For non sortable columns use empty
    # value like ''
    order_columns = columns
    # define the columns that will be returned

    # set max limit of records returned, this is used to protect our site if someone tries to attack our site
    # and make it return huge amount of data
    max_display_length = 500

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.all().order_by('-time')
    

class TransactionDetailView(LoginRequiredMixin,DetailView):
    login_url = 'hub/login/'
    template_name  = 'FinanceAPI/transaction_detail.html'
    context_object_name = 'transaction'

    def get_object(self):
        id = self.kwargs.get("id")
        return get_object_or_404(models.Transaction, id=id)



class CreateTransactionView(CreateView):
    model = models.Transaction
    form_class = forms.TransactionModelForm

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class EditTransactionView(UpdateView):
    model = models.Transaction


class CreateTransactionTypeView(CreateView):
    model = models.TransactionType