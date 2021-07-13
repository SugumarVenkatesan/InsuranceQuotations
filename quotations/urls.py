from django.urls import path

from quotations import views

app_name = 'Quotations'

urlpatterns = [
    path('', views.QuotationListView.as_view(), name='quotations'),
    path('<int:id>', views.QuotationDetailView.as_view(),
         name='quotation_detail'),
    path('create/', views.QuotationCreateView.as_view(), name='create'),
]
