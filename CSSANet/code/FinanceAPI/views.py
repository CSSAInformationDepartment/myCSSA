from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib.auth.mixins import  LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from django.contrib.auth.decorators import login_required, permission_required

from FinanceAPI import models, forms



class TransactionListView(LoginRequiredMixin,ListView):
    paginate_by = 25
    login_url = 'hub/login/'
    template_name  = 'FinanceAPI/transaction_list.html'
    queryset = models.Transaction.objects.all().order_by('time')
    context_object_name = 'transaction_list'

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