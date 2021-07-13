from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'Quotation API'

urlpatterns = [
    path('coverages/', views.CoverageView.as_view(), name='coverages'),
    path('', views.QuotationList.as_view(), name='quotations'),
    path('<int:id>', views.QuotationDetail.as_view(), name='quotation_detail'),
    path('create/', views.QuotationList.as_view(), name='create'),
    path('api-token-auth/', obtain_auth_token, name='api-token-auth')
]
