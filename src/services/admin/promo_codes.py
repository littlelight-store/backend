from django.contrib import admin

from .. import models


class PromoCodeAdminView(admin.ModelAdmin):
    pass


admin.site.register(models.PromoCode, PromoCodeAdminView)
