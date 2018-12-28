from django import forms
from FinanceAPI import models


class TransactionModelForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = ['transaction_type','is_expense', 'amount', 'note']

class TransactionTypeModelForm(forms.ModelForm):   
    class Meta:
        model = models.TransactionType
        fields = ['name',]

class InvoiceModelForm(forms.ModelForm):   
    class Meta:
        model = models.Invoice
        fields = ['abn_number','amount','note','pic_scan']

class BankTransferRecipientModelForm(forms.ModelForm):   
    class Meta:
        model = models.BankTransferRecipient
        fields = ['bsb','acc_number','amount','note','pic_scan']