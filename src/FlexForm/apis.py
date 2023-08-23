from .forms import *


def flexform_user_write_in(user, field_data):
    if isinstance(field_data, dict):
        for k, v in field_data.items():
            submit = FlexFormData(
                field=FlexFormField.objects.get(pk=k),
                value=v,
                user=user,
            )
            submit.save()
            return True
    else:
        return False
