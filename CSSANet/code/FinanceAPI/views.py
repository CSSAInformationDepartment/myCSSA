from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.mixins import  LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from django_datatables_view.base_datatable_view import BaseDatatableView
from django.utils.html import escape

from FinanceAPI import models, forms


class TransactionListView(LoginRequiredMixin, View):
    login_url = '/hub/login/'
    template_name = 'FinanceAPI/transaction_list.html'

    #请求处理函数 （get）
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

class TransactionListJson(LoginRequiredMixin, PermissionRequiredMixin, BaseDatatableView):
    login_url = '/hub/login/'
    permission_required = ('can_view_transaction',)
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

    def render_column(self, row, column):
        # Customer HTML column rendering
        if column == 'is_effective':
            if row.is_effective:
                return '<span class="badge badge-success">已核验</span>'
            else:
                return '<span class="badge badge-warning">未核验</span>'
        elif column == 'is_expense':
            if row.is_expense:
                return escape('支出')
            else:
                return escape('收入')
        elif column == 'time':
            return escape(row.time.strftime('%Y/%m/%d %H:%M:%S'))
        elif column == 'amount':
            return escape('AUD $'+ str(row.amount))
        else:
            return super(TransactionListJson, self).render_column(row, column)

    def get_initial_queryset(self):
        if not self.model:
            raise NotImplementedError("Need to provide a model or implement get_initial_queryset!")
        return self.model.objects.all().order_by('-time')

    def filter_queryset(self, qs):
        # DO NOT CHANGE THIS LINE
        search = self.request.GET.get('search[value]', None)

        if search:
            qs = qs.filter(related_user__email__istartswith=search)
        return qs


class TransactionDetailView(LoginRequiredMixin,View):
    login_url = 'hub/login/'
    template_name  = 'FinanceAPI/transaction_detail.html'
    #context_object_name = 'record'

    #def get_object(self):
    #    id = self.kwargs.get("id")
    #    return get_object_or_404(models.Transaction, id=id)

    def get(self, request, *args, **kwargs):
        id = self.kwargs.get('id')
        try:
            transaction_query = models.Transaction.objects.get(id=id)
            invoice = models.Invoice.objects.filter(related_transaction=id).first()
            bankstate = models.BankTransferRecipient.objects.filter(related_transaction=id).first()
        except transaction_query.model.DoesNotExist:
            raise Http404('No %s matches the given query.' % transaction_query.model._meta.object_name)

        return render(request, self.template_name, {'record':transaction_query, 'invoice':invoice, 'bankstate':bankstate})

class LodgeInvoiceView(View):
    template_name  = 'FinanceAPI/invoice_lodge.html'

    def get(self, request, *args, **kwargs):
       personal_lodge = models.Invoice.objects.filter(uploader=request.user.id).order_by('-time')
       form = forms.InvoiceModelForm
       return render(request, self.template_name, {'record':personal_lodge, 'form':form })

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
