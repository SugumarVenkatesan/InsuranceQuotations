from django.contrib.auth.models import User
from django.contrib.auth import login
from django.http.response import HttpResponseRedirect
import requests
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from . import forms
from django.conf import settings
import json
import decimal


class QuotationListView(ListView):

    """
    List of all the :model:`Quotation` made by the connected :model:`Customer`
    Click on a row to get the quotation detail
    :template:`quotation/quotation_list.html`
    """
    template_name = 'quotations/quotation_list.html'

    def get(self, request):
        headers = {}
        if request.user.is_authenticated and request.user.auth_token:
            headers = {'Authorization': 'Token ' +
                       str(request.user.auth_token)}
            jsonResponse = requests.get(
                settings.QUOTATION_API_BASE_URL, headers=headers).json()

            return render(request, self.template_name,
                          {'quotations': jsonResponse,
                           'userConnected': request.user})
        return render(request, self.template_name,
                          {'quotations': {},
                           'userConnected': request.user})


class QuotationDetailView(DetailView):
    """
    Display an invidicual :model:`Quotation`
    TODO email generation from this page
    template name :template:`quotations/quotation.html`
    """
    template_name = 'quotations/quotation.html'

    def get(self, request, id):
        """
        get method to retrieve the quotation
        """
        response = requests.get(settings.QUOTATION_API_BASE_URL + str(id))

        return render(request, self.template_name,
                      {'quotation': response.json(),
                       'userConnected': request.user})


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        super(DecimalEncoder, self).default(o)


class QuotationCreateView(CreateView):
    """
    Form for :model:`Quotation creation`
    Automtically generate the email
    TODO do this in the detail view
    """
    template_name = 'quotations/create.html'
    createform = forms.QuotationForm

    def post(self, request):
        """
        Validate and send a post request to the API
        """
        self.createform = forms.QuotationForm(request.POST)
        if self.createform.is_valid():
            req = {
                "name": self.createform.cleaned_data['name'],
                "email": self.createform.cleaned_data['email'],
                "phone": self.createform.cleaned_data['phone'],
                "vehicleModel": self.createform.cleaned_data['vehicleModel'],
                "vehicleYearMake": self.createform.cleaned_data['vehicleYearMake'],
                "vehicleNumber":  self.createform.cleaned_data['vehicleNumber'],
                "vehiclePrice": self.createform.cleaned_data['vehiclePrice'],
                "covWind": self.createform.cleaned_data['covWind'],
                "covPass": self.createform.cleaned_data['covPass'],
                "covFlood": self.createform.cleaned_data['covFlood']
            }
            response = requests.post(settings.QUOTATION_API_BASE_URL + 'create/',
                                     data=json.dumps(req, cls=DecimalEncoder),
                                     headers={'Content-type': 'Application/json'})
            if response.status_code == 201:
                reponseJson = response.json()
                quotationCreatedId = reponseJson['id']
                userFromJson = reponseJson['customer']
                user = User.objects.filter(username=userFromJson['username'])
                login(self.request, user.first())
                return HttpResponseRedirect('/quotation/' +
                                            str(quotationCreatedId))

        return render(request, self.template_name, {'form': self.createform})

    def get(self, request):
        """
        Initialize the form for `:model:`Quotation creation via API
        """
        if not request.user.is_anonymous and request.user.customer:
            self.createform.base_fields['name'].initial = request.user.customer.last_name
            self.createform.base_fields['email'].initial = request.user.customer.username
            self.createform.base_fields['phone'].initial = request.user.customer.phone
        return render(request, self.template_name, {'form': self.createform,
                                                    'userConnected': request.user})
