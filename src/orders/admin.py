from django.contrib import admin
from django_transitions.admin import WorkflowAdminMixin

from .orm_models import ORMClientOrder, ORMOrderObjective, ORMShoppingCart, ORMShoppingCartItem, ChatMessage


class CartItemStacked(admin.StackedInline):
    extra = 0
    model = ORMShoppingCartItem


class CartAdminModel(admin.ModelAdmin):
    inlines = [CartItemStacked]
    list_display = ["__str__", "created_at"]


admin.site.register(ORMShoppingCart, CartAdminModel)


class OrderObjectiveAdminStacked(admin.StackedInline):
    extra = 0
    model = ORMOrderObjective


class ClientOrderAdminModel(admin.ModelAdmin):
    inlines = [OrderObjectiveAdminStacked]
    list_display = ["__str__", "total_price", "client", "order_status", "created_at"]


admin.site.register(ORMClientOrder, ClientOrderAdminModel)


class OrderObjectiveAdminModel(WorkflowAdminMixin, admin.ModelAdmin):
    list_display = ['__str__', 'service', 'get_client', 'status', 'price', 'created_at', 'booster']
    list_editable = ['booster']

    @staticmethod
    def get_client(obj):
        return obj.client_order.client if obj.client_order else None


admin.site.register(ORMOrderObjective, OrderObjectiveAdminModel)


class ChatMessagesAdminModel(admin.ModelAdmin):
    pass


admin.site.register(ChatMessage, ChatMessagesAdminModel)
