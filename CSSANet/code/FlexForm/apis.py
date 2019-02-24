from .forms import *

def flexform_user_write_in(user, field_data):
    if isinstance(field_data,dict):
        for k,v in field_data.items():
            submit = UserWriteInForm(initial={
                'field':k,
                'value':v,
                'user':user,
            })
            if submit.is_valid():
                submit.save()
            else:
                print(submit.errors)
                return False
    else:
        return False