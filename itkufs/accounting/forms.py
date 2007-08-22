from datetime import datetime

from django import newforms as forms
from django.db.models import Q

from itkufs.accounting.models import *
from itkufs.widgets import *

all_choices = [(False, (('',''),))]
user_choices = [(False, (('',''),))]
group_choices = [(False, (('',''),))]

for g in AccountGroup.objects.all():
    all_accounts = []
    user_accounts = []
    group_accounts = []
    for a in g.account_set.all():
        all_accounts.append((a.id, a.name))
        if a.is_user_account():
            user_accounts.append((a.id, a.name))
        else:
            group_accounts.append((a.id, a.name))
    all_choices.append((g.name, all_accounts))
    group_choices.append((g.name, group_accounts))
    user_choices.append((g.name, user_accounts))

amount_field = forms.DecimalField(required=True)
details_field = forms.CharField(widget=forms.widgets.Textarea(attrs={'rows':2}), required=False)

#FIXME http://www.djangoproject.com/documentation/newforms/#subclassing-forms

class TransactionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        def _get_choices(options={}):
            limit_groups = options.pop('limit_to_groups', ())
            exclude_users = options.pop('exclude_users', ())
            user_account = options.pop('user_accounts', False)
            exclude_groups = options.pop('exclude_groups', ())
            group_account = options.pop('group_accounts', False)

            # FIXME Clean up code please
            # FIXME exlcude user not working yet...
            if limit_groups and exclude_groups:
                groups = AccountGroup.objects.filter(
                    pk__in=[g.id for g in limit_groups]).exclude(
                    pk__in=[g.id for g in exclude_groups])
            elif limit_groups:
                groups = AccountGroup.objects.filter(
                    pk__in=[g.id for g in limit_groups])
            elif exclude_groups:
                groups = AccountGroup.objects.exclude(
                    pk__in=[g.id for g in exclude_groups])
            else:
                groups = AccountGroup.objects.all()

            choices = [(False, (('',''),))]
            for g in groups:
                a_choices = []
                for a in g.account_set.all():
                    if (a.is_user_account() and user_account) or (not a.is_user_account() and group_account):
                        a_choices.append((a.id, a.name))
                if a_choices:
                    choices.append((g.name, a_choices))
            return choices

        to_options = kwargs.pop('to_options', {})
        from_options = kwargs.pop('from_options', {})
        super(TransactionForm, self).__init__(*args, **kwargs)

        self.fields['to_account'].choices = _get_choices(to_options)
        self.fields['from_account'].choices = _get_choices(from_options)


    to_account = GroupedChoiceField(label="To", required=True)
    from_account = GroupedChoiceField(label="From", required=True)
    amount = amount_field
    payed = forms.BooleanField(required=False)
    details = details_field

class DepositWithdrawForm(forms.Form):
    amount = amount_field
    details = details_field

class TransferForm(forms.Form):
    # FIXME should only give choices for people in same group
    to_account = GroupedChoiceField(choices=user_choices, label="To", required=True)
    amount = amount_field
    details = details_field
