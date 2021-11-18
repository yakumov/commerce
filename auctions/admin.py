from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Lot, LotImage, LotCategory, Bid

# Register your models here.

class LotAdmin(admin.ModelAdmin):
    list_display = ("lot_name", "lot_price", "lot_description", "lot_date", "lot_status", "lot_author", "lot_category", "lot_viewimage", "lot_bid")


admin.site.register(User, UserAdmin)
admin.site.register(Lot, LotAdmin)
admin.site.register(LotImage)
admin.site.register(Bid)
admin.site.register(LotCategory)


