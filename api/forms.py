from django.forms.models import ModelForm
from . import models
from django import forms


class QuotationForm(ModelForm):
    """
    Form for `:model:`Quotation creation
    View : `:view:`QuotationCreateView
    """

    name = forms.CharField(max_length=30)
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)

    class Meta:
        model = models.Quotation
        fields = ['name', 'email', 'phone', 'vehicleYearMake',
                  'vehicleModel', 'vehicleNumber', 'vehiclePrice',
                  'covWind', 'covPass', 'covFlood',
                  ]
