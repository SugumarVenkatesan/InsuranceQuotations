
from api import serializers
from api.models import Coverage, Customer, Quotation
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.authtoken.models import Token

# Views utilized by Api


class CoverageView(generics.ListAPIView):
    """
    Return all the :model:`coverage` from the database
    GET only
    """
    queryset = Coverage.objects.all()
    serializer_class = serializers.CoverageSerializer


class QuotationDetail(generics.RetrieveAPIView):
    """
    Return a :model:`quotation` with details by its id
    """
    serializer_class = serializers.QuotationSerializer
    queryset = Quotation.objects.all()
    lookup_field = 'id'


class QuotationList(generics.ListCreateAPIView):
    """
    Get : list of all the :model:`quotation`
    Post : create a new :model:`quotation` with :model:`customer` creation if not yet in the :model:`auth.user` base.
    The email adress is used for Customer creation
    """
    queryset = Quotation.objects.all()
    serializer_class = serializers.QuotationSerializer

    def get(self, request):
        """
        Manual auth verification : if no user, returns empty list, if user autenthicated returns his quotations
        """
        if request.user.is_authenticated:
            self.queryset = Quotation.objects.filter(
                customer__username=request.user.username)
        else:
            self.queryset = []

        return self.list(request)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            quotation = Quotation.objects.get(pk=serializer.instance.id)
            quotation.quotationPrice = quotation.compute_quotation_price()
            quotation.save()
            return Response(data=self.get_serializer(quotation).data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        cust = self.get_by_email_or_create()
        serializer.save(customer=cust)

    def get_by_email_or_create(self):
        """
        Retrieve the :model:`customer` with the email inputed or create a new one
        """
        mail = self.request.data['email']
        cust = Customer.objects.filter(username__icontains=mail)
        if cust:
            return cust.first()

        # No user ? create one
        cust = Customer.objects.create(
            username=mail,
            last_name=self.request.data['name'],
            email=mail,
            phone=self.request.data['phone']
        )
        cust.set_password('Tigerlab@2021')
        # create token
        Token.objects.create(user=cust)
        cust.save()
        return cust
