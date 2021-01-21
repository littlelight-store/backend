import copy

from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.contrib.postgres.fields import JSONField
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.urls import reverse
from django_object_actions import DjangoObjectActions
from prettyjson import PrettyJSONWidget

from .. import models


class PromoCodesAdminInline(admin.TabularInline):
    model = models.PromoCode.service.through


class ServicesConfigsAdminView(admin.TabularInline):
    model = models.ServiceConfig


class ServicesAdminView(SortableAdminMixin, DjangoObjectActions, admin.ModelAdmin):
    inlines = [
        ServicesConfigsAdminView,
        PromoCodesAdminInline
    ]

    list_display = ('slug', 'title', 'category')

    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }

    def get_queryset(self, request):
        qs = super(ServicesAdminView, self).get_queryset(request)
        return qs.filter(category__site=get_current_site(request))

    def copy_object(self, request, obj):

        new_instance = copy.deepcopy(obj)
        new_instance.pk = 'new-object'
        new_instance.ordering = 0
        new_instance.save()

        url = reverse('admin:%s_%s_change' % (new_instance._meta.app_label, new_instance._meta.model_name), args=[new_instance.pk])

        return HttpResponseRedirect(url)

    copy_object.label = "Copy object"  # optional
    copy_object.short_description = "Creates new object with new-object slug"  # optional

    change_actions = ('copy_object', )


admin.site.register(models.Service, ServicesAdminView)


class ServiceGroupTagAdminView(SortableAdminMixin, admin.ModelAdmin):
    fields = ('value', 'name', 'services')


admin.site.register(models.ServiceGroupTagORM, ServiceGroupTagAdminView)
