from django.contrib import admin

import FinanceAPI.models as Models

# Register your models here.


class AccountBalanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'time', 'amount')
    list_display_links = ('id',)
    search_fields = ('id',)
    list_per_page = 25


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'time', 'is_effective',
                    'transaction_type', 'is_expense', 'amount')
    list_display_links = ('id',)
    search_fields = ('id', 'time', 'is_effective')
    list_per_page = 25


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'time', 'abn_number', 'uploader')
    list_display_links = ('id',)
    search_fields = ('id', 'time', 'abn_number', 'uploader__email')
    list_per_page = 25


class BankTransferRecipientAdmin(admin.ModelAdmin):
    list_display = ('id', 'time', 'acc_number', 'bsb', 'sender')
    list_display_links = ('id',)
    search_fields = ('id', 'time', 'acc_number', 'bsb', 'sender__email')
    list_per_page = 25


admin.site.register(Models.AccountBalance, AccountBalanceAdmin)
admin.site.register(Models.Transaction, TransactionAdmin)
admin.site.register(Models.TransactionType)
admin.site.register(Models.TransactionReview)
admin.site.register(Models.Invoice, InvoiceAdmin)
admin.site.register(Models.BankTransferRecipient, BankTransferRecipientAdmin)
