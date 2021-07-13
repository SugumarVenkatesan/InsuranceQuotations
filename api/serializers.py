from rest_framework.fields import SerializerMethodField
from rest_framework import serializers
from api.models import Coverage, Quotation, Customer


class CoverageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Coverage
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ['username', 'last_name', 'email', 'phone']


class QuotationSerializer(serializers.ModelSerializer):

    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Quotation

        fields = ['customer', 'id', 'vehicleYearMake', 'vehicleModel',
                  'vehicleNumber', 'vehiclePrice', 'quotationPrice',
                  'covWind', 'covPass', 'covFlood', 'created',
                  'short_creation_date']
