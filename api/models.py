from django.db import models
from django.contrib.auth import models as authModel
from django.core.validators import MinValueValidator
from django.template.defaultfilters import date
from io import BytesIO
from reportlab.pdfgen import canvas
from django.core.mail import EmailMessage
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
import decimal


class Customer (authModel.User):
    """
    Extends django User object to be able to store the phone number
    Related to :model:`auth.user`
    """

    phone = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.last_name + ' (' + self.username + ')'


class Coverage(models.Model):
    """
    Store the coverages used in the app including code (name), description and default price
    Not related to any other object
    Do not change the codes : WIND, PASS, FLOOD as they're used in the app 
    """
    name = models.CharField(max_length=8, primary_key=True)
    description = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.name} : {self.description} - actual price : RM {str(self.price)}'


def get_coverage_price_by_name(covname):
    """
    Utility method to retrieve default coverage price by its code (name)
    """
    try:
        obj = Coverage.objects.get(name=covname)
    except ObjectDoesNotExist:
        return decimal.Decimal('0')
    return obj.price


class Quotation(models.Model):
    """
    Stores all the quotations made with the app
    related to :model: `customer`
    """
    BOOL_CHOICES = ((True, 'Yes'), (False, 'No'))

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="quotations")
    vehicleYearMake = models.PositiveSmallIntegerField(default=2021)
    vehicleModel = models.CharField(max_length=80)
    vehicleNumber = models.CharField(max_length=30)
    vehiclePrice = models.DecimalField(
        max_digits=10, decimal_places=2, default=100_000,
        validators=[MinValueValidator(30_000)])
    quotationPrice = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, editable=False)
    covWind = models.BooleanField(choices=BOOL_CHOICES,
                                  default=False, verbose_name="Windscreen coverage")
    covPass = models.BooleanField(choices=BOOL_CHOICES,
                                  default=False,
                                  verbose_name="Passenger liability coverage")
    covFlood = models.BooleanField(choices=BOOL_CHOICES,
                                   default=False,
                                   verbose_name="Flood, Windstorm,Landslide or Subsidence coverage")
    created = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        """
        get the url of the rendering template from urls.py
        """
        return reverse('quotation', kwargs={'pk': self.pk})

    def __str__(self):
        """
        Mainly used for quotation-admin and clean display 
        """
        return f'{self.short_creation_date} - {self.customer.username} - {self.vehicleModel} - {self.quotationPrice}'
        

    @property
    def short_creation_date(self):
        """
        Shorten the timestamp
        """
        return date(self.created, "j/n/Y")

    def calculate_and_save(self):
        """
        Updates the quotation price
        """
        # Calculate the quotation price
        self.quotationPrice = self.compute_quotation_price()
        self.save()

    def compute_quotation_price(self):
        """
        Calculates the quotation price applying the given rules
        """
        result = decimal.Decimal('0')
        if self.vehiclePrice:
            result = self.vehiclePrice * 2 / 100
        if self.covWind:
            result += get_coverage_price_by_name("WIND")
        if self.covPass:
            result += get_coverage_price_by_name("PASS")
        if self.covFlood:
            result += get_coverage_price_by_name("FLOOD")
        return result

    def generate_pdf(self):
        """
        TODO generate the content a the quotation pdf
        """
        x = 100
        y = 100
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize="A4")
        p.drawString(x, y, "TO DO")
        p.showPage()
        p.save()
        pdf = buffer.getvalue()
        buffer.close()
        return pdf

    def send_email(self):
        """
        Generate an email with the quotation pdf attached
        Has to be configured in settings.py
        """
        EmailMsg = EmailMessage("Your quotation", "Please find the attached quotation requested", 'no-reply@quotationagent.com', [
            self.customer.email], headers={'Reply-To': 'no-reply@quotationagent.com'})
        pdf = self.generate_pdf()
        EmailMsg.attach('quotation.pdf', pdf, 'application/pdf')
        EmailMsg.send(fail_silently=False)
