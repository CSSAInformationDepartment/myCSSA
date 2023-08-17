from .models import *


def lodge_sys_gen_transaction(related_user, type='Default', is_effective=True, amount=None, is_expense=False, note=None):
    transaction_type = TransactionType.objects.get_or_create(
        name=type
    )
    if amount:
        new_transaction = Transaction(
            transaction_type=transaction_type[0],
            related_user=related_user,
            amount=amount,
            is_expense=is_expense,
            note=note,
        )

        new_transaction.save()

        new_transaction_review = TransactionReview(
            transaction=new_transaction,
            is_auto_created=True,
            is_approved=True,
            note=None
        )

        new_transaction_review.save()

        return new_transaction

    return False
