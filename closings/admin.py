from django.contrib import admin
from .models import Deal, Document, Signature, Signer

# Register your models here.
# admin.register([Deal, Document, Signature, Signer])
admin.site.register([Deal, Document, Signature, Signer])