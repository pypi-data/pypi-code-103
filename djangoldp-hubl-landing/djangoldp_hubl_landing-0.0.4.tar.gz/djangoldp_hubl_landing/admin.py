from django.contrib import admin
from djangoldp.admin import DjangoLDPAdmin
from djangoldp.models import Model
from djangoldp_hubl_landing.models import ClientContact, JoinContact, GeneralContact


class ContactAdmin(DjangoLDPAdmin):
    search_fields = ['name']

class ClientAdmin(DjangoLDPAdmin):
    list_display = ('name', 'firstname', 'companyname', 'city')
    search_fields = ['name', 'city', 'companyname']

class JoinAdmin(DjangoLDPAdmin):
    list_display = ('name', 'firstname', 'city')
    search_fields = ['name', 'city']

admin.site.register(ClientContact, ClientAdmin)
admin.site.register(JoinContact, JoinAdmin)
admin.site.register(GeneralContact, ContactAdmin)
