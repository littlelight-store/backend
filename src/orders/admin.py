from django.contrib import admin
from django_transitions.admin import WorkflowAdminMixin

from .orm_models import ORMClientOrder, ORMOrderObjective, ORMShoppingCart, ORMShoppingCartItem


class CartItemStacked(admin.StackedInline):
    extra = 0
    model = ORMShoppingCartItem


class CartAdminModel(admin.ModelAdmin):
    inlines = [CartItemStacked]


admin.site.register(ORMShoppingCart, CartAdminModel)


class OrderObjectiveAdminStacked(admin.StackedInline):
    extra = 0
    model = ORMOrderObjective


class ClientOrderAdminModel(admin.ModelAdmin):
    inlines = [OrderObjectiveAdminStacked]


admin.site.register(ORMClientOrder, ClientOrderAdminModel)


class OrderObjectiveAdminModel(WorkflowAdminMixin, admin.ModelAdmin):
    pass


admin.site.register(ORMOrderObjective, OrderObjectiveAdminModel)


