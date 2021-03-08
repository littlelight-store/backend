from django.contrib import admin

from .models import BoosterUser, BungiePlatform, ProfileCredentials, User, BungieID

# Register your models here.
from .orm_models import ORMDestinyBungieProfile


class ProfileCredentialsInline(admin.StackedInline):
    model = ProfileCredentials


class DestinyProfleInline(admin.StackedInline):
    model = ORMDestinyBungieProfile


class UserInlineAdmin(admin.ModelAdmin):
    model = User

    inlines = [
        ProfileCredentialsInline,
        DestinyProfleInline
    ]


class UserInline(admin.StackedInline):
    model = User


admin.site.register(User, UserInlineAdmin)


class BoostingUserAdmin(admin.ModelAdmin):
    def __str__(self):
        return "Booster User"

    inlines = [
        UserInline
    ]


admin.site.register(BoosterUser, BoostingUserAdmin)
admin.site.register(BungiePlatform)
admin.site.register(BungieID)


@admin.register(ProfileCredentials)
class ProfileCredentialsAdmin(admin.ModelAdmin):
    pass


@admin.register(ORMDestinyBungieProfile)
class NewORMDestinyBungieProfile(admin.ModelAdmin):
    pass
