from datetime import datetime
from django.test import TestCase
from django.db.utils import IntegrityError
import decimal


from . import models


class CustomerModelTests(TestCase):
    """
    Some very basic tests as a beginning
    """

    def setUp(self):
        self.mod = models.Customer.objects.create(
            username="email@email.com", last_name="test", phone="0102030405")

    def test_written_in_db(self):
        self.assertEquals(models.Customer.objects.count(), 1)

    def test_phone_is_not_too_long(self):
        tmp = models.Customer.objects.first()
        tmp.phone = "1234567890"*9
        tmp.save()
        # so i can save a too long phone number ?
        self.assertEquals(len(tmp.phone), 90)

    def test_str_for_customer(self):
        self.assertEquals(str(self.mod), "test (email@email.com)")


class CoverageModelTests(TestCase):

    def setUp(self):
        self.mod = models.Coverage.objects.create(name="TEST",
                                                  description="coverage description", price=154.89)

    def test_str_for_coverage(self):
        self.assertEquals(
            str(self.mod), "TEST : coverage description - actual price : RM 154.89")


class QuotationModelTests(TestCase):

    def setUp(self):
        self.cust = models.Customer.objects.create(
            username="test", email="email@email.com", phone="0102030405")
        self.mod = models.Quotation.objects.create(
            customer=self.cust, vehicleModel="MODEL", quotationPrice=234.989)

    def test_missing_customer_constraint(self):
        newObj = models.Quotation()
        with self.assertRaises(IntegrityError):
            newObj.save()

    def test_str_for_quotation(self):
        now = datetime.now()
        try:
            #OSX or Unix
            nowstr = now.strftime('%-d/%-m/%Y')  # with no zero-padded
        except ValueError:
            # Windows
            nowstr = now.strftime('%#d/%#m/%Y')  # with no zero-padded
            
        self.assertEquals(str(self.mod), nowstr +
                          " - test - MODEL - 234.989")

    def test_has_timeStamp(self):
        self.assertIsInstance(self.mod.created, datetime)

    def test_short_date_month_with_zero(self):
        date_time_obj = datetime.strptime("28/02/2020", '%d/%m/%Y')
        self.mod.created = date_time_obj
        self.assertEquals(self.mod.short_creation_date, "28/2/2020")

    def test_short_date_day_with_zero(self):
        date_time_obj = datetime.strptime("07/10/2020", '%d/%m/%Y')
        self.mod.created = date_time_obj
        self.assertEquals(self.mod.short_creation_date, "7/10/2020")

    def test_save_and_calculate_no_id(self):
        newObj = models.Quotation()
        # Customer is mandatory
        newObj.customer = models.Customer.objects.create(
            username="user", id=999)
        newObj.calculate_and_save()
        self.assertIsNotNone(newObj.id)

    def test_compute_price_no_price_no_coverage(self):
        # Given
        self.mod.vehiclePrice = 0
        # When
        price = self.mod.compute_quotation_price()
        # Then
        self.assertEquals(price, 0)

    def test_compute_price_a_price_no_coverage(self):
        # Given
        self.mod.vehiclePrice = 100
        # When
        price = self.mod.compute_quotation_price()
        # Then
        self.assertEquals(price, 2)

    def test_compute_price_no_price_WIND_coverage(self):
        # Given
        self.mod.vehiclePrice = decimal.Decimal('0')
        models.Coverage.objects.create(name="WIND",
                                       description="cov500",
                                       price=decimal.Decimal('500'))
        self.mod.covWind = True
        # When
        price = self.mod.compute_quotation_price()
        # Then
        self.assertEquals(price, 500)

    def test_compute_price_no_price_PASS_coverages(self):
        # Given
        self.mod.vehiclePrice = decimal.Decimal('0')
        models.Coverage.objects.create(name="PASS",
                                       description="cov100",
                                       price=decimal.Decimal('100'))
        self.mod.covPass = True
        # When
        price = self.mod.compute_quotation_price()
        # Then
        self.assertEquals(price, 100)

    def test_compute_price_no_price_FLOOD_coverages(self):
        # Given
        self.mod.vehiclePrice = 0
        models.Coverage.objects.create(name="FLOOD",
                                       description="cov0",
                                       price=decimal.Decimal('0'))
        self.mod.covFlood = True
        # When
        price = self.mod.compute_quotation_price()
        # Then
        self.assertEquals(price, 0)

    def test_compute_price_a_price_all_coverage(self):
        # Given
        self.mod.vehiclePrice = decimal.Decimal('100000')
        models.Coverage.objects.create(name="WIND",
                                       description="cov500",
                                       price=decimal.Decimal('500'))
        self.mod.covWind = True
        models.Coverage.objects.create(name="PASS",
                                       description="cov100",
                                       price=decimal.Decimal('100'))
        self.mod.covPass = True
        models.Coverage.objects.create(name="FLOOD",
                                       description="cov0",
                                       price=decimal.Decimal('0'))
        self.mod.covFlood = True
        # When
        price = self.mod.compute_quotation_price()
        # Then
        # Price = 100000*2% + 500 + 100 + 0
        self.assertEquals(price, 2600)
