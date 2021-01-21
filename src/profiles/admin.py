from django.contrib import admin

from .models import BoosterUser, BungiePlatform, ProfileCredentials, User

# Register your models here.
from .orm_models import ORMDestinyBungieProfile


class ProfileCredentialsInline(admin.StackedInline):
    model = ProfileCredentials


class UserInlineAdmin(admin.ModelAdmin):
    model = User

    inlines = [
        ProfileCredentialsInline
    ]


admin.site.register(User, UserInlineAdmin)


class BoostingUserAdmin(admin.ModelAdmin):
    def __str__(self):
        return "Booster User"


admin.site.register(BoosterUser, BoostingUserAdmin)
admin.site.register(BungiePlatform)


@admin.register(ProfileCredentials)
class ProfileCredentialsAdmin(admin.ModelAdmin):
    fields = [
        "account_name",
        "account_password",
        "owner",
        "platform"
    ]


@admin.register(ORMDestinyBungieProfile)
class NewORMDestinyBungieProfile(admin.ModelAdmin):
    pass
