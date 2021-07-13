
from django.contrib import admin, messages
from django.contrib.admin.sites import AdminSite
from django.utils.translation import ngettext

from . import models

# Models in the regular admin
#FIXME "Customer" is currently displayed as "User" in Admin
myModels = [models.Coverage, models.Customer, models.Quotation]
myLibs = ['Coverage', 'Customer', 'Quotation']
admin.site.register(myModels)


class QuotationAdminSite(AdminSite):
    """
    Quotation Admin Site specific
    """
    site_header = "Quotations view by Agent"
    site_title = "Quotation Admin"


quotAdmin = QuotationAdminSite(name='quotAdmin')


class QuotationModelAdmin(admin.ModelAdmin):
    list_display = ['customer', 'vehicleModel',
                    'vehiclePrice', 'quotationPrice', 'created']
    ordering = ['created']
    search_fields = ['vehicleModel']
    actions = ['send_emails', 'refresh_quotation_price']

    @admin.action(description='Send email to user')
    def send_emails(self, request, queryset):
        for q in queryset:
            q.send_email()
        self.message_user(request, ngettext(
            '%d email was successfully sent.',
            '%d emails were successfully sent.',
            len(queryset),
        ) % len(queryset), messages.SUCCESS)

    @admin.action(description='Refresh quotation price')
    def refresh_quotation_price(self, request, queryset):
        for q in queryset:
            q.quotationPrice = q.compute_quotation_price()
            q.save()

        self.message_user(request, ngettext(
            '%d quotation was successfully updated.',
            '%d quotation were successfully updated.',
            len(queryset),
        ) % len(queryset), messages.SUCCESS)


quotAdmin.register(models.Quotation, QuotationModelAdmin)
