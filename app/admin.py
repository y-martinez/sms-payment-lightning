from django.contrib import admin
from .models import User, Wallet, Payment, Invoice


admin.site.register(User)
admin.site.register(Wallet)
admin.site.register(Payment)
admin.site.register(Invoice)
