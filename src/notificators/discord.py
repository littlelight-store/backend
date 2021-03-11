import datetime as dt

from discord import Colour, Embed, RequestsWebhookAdapter, Webhook
from pydantic import BaseModel

from core.application.repositories.notifications import (
    OrderCreatedDTO,
    OrderExecutorsNotificationRepository,
)
from notificators.constants import Category
from profiles.constants import Membership

BOT_NAME = '⚙️ LittleLight.orders'

web_hooks = {
    Membership.PS4: {
        Category.pvp: "740212466075697224/qjSbaPixzaXbxAHUbEBC2tp-QNrIcGOhiHNiMHKoIUoa4R8x9HNDZdM1aDMZM4AYX2WO",
        Category.pve: "740212589652344882/mqCFkk7gLNj3s4YIFydRH1U1OzPj9tiveXI1BijouCaIA_NwIpdI8UZxgld2dgg0N9WyA"
    },
    Membership.Xbox: {
        Category.pvp: "740213043866239109/GGj3fQG1womgUTunuuK-BkLkNs82HAZAXLePiiHvMAni9fKb1_THddg7vPo_AjO3pfuW",
        Category.pve: "740213145804603473/cx_R3jekwg9Sy_HeX1wcpcKcMvgT225wCX3rqNp-iTYWzbloA8Gz6IyFnmcDHKyx0OvF"
    },
    Membership.Steam: {
        Category.pvp: "740213234216468491/pK0dA87aKFrLxw6hl96YI7XOW6bnfUDQ481htf2NIzkwwTKtTv4yg50VyP1y6c2V8W8w",
        Category.pve: "740213339526791228/0h7ALbYov8TT9jXOCkETT2hmyIZRkcI2ie7eKTpuSb7e4rwtZ6eSmZpUn8pqdb4YaCYe"
    }
}


class MessageBuilderParamsDTOOutput(BaseModel):
    content: str
    embed: Embed

    class Config:
        arbitrary_types_allowed = True


class NewMessageBuilder:
    def _create_embed(self, dto: OrderCreatedDTO):
        embed = Embed(
            title=f'[{dto.order_id}] *{dto.service_title}*',
            colour=Colour.green(),
            timestamp=dt.datetime.utcnow(),
        )

        for service in dto.selected_services:
            embed.add_field(name='🚩', value=service.description, inline=True)

        embed.add_field(name='💰', value=f'*${dto.booster_price}*', inline=False)

        embed.add_field(name='Add any reaction to accept an order', value=f'😉', inline=False)

        embed.set_footer(text='LittleLight.store')

        return embed

    def execute(self, dto: OrderCreatedDTO) -> MessageBuilderParamsDTOOutput:
        return MessageBuilderParamsDTOOutput(
            content=f'',
            embed=self._create_embed(dto)
        )


def _get_channels_category(category: str) -> Category:
    if category == 'pvp':
        return Category.pvp
    else:
        return Category.pve


def webhook_factory(platform: Membership, category: Category):
    web_hook = web_hooks[platform][category]

    return Webhook.from_url(f"https://discordapp.com/api/webhooks/{web_hook}", adapter=RequestsWebhookAdapter())


# class DiscordNotificator(OrderExecutorsNotificationRepository):
#     def __init__(
#         self,
#         message_builder: type(MessageBuilder) = MessageBuilder,
#         _web_hook_factory=webhook_factory
#     ):
#
#         self.message_builder = message_builder
#         self._web_hook_factory = _web_hook_factory
#
#     def order_created(self, parent_order: ParentOrder):
#         for order in parent_order.orders:
#             channel_category = _get_channels_category(order.service.category)
#             web_hook = self._web_hook_factory(parent_order.platform, category=channel_category)
#
#             message = self.message_builder().set_params(order=order, parent_order=parent_order).execute()
#
#             web_hook.send(message.content, username=BOT_NAME, embed=message.embed)


class NewDiscordNotificator(OrderExecutorsNotificationRepository):
    def __init__(
        self,
        message_builder: type(NewMessageBuilder),
        _web_hook_factory=webhook_factory,
    ):
        self._web_hook_factory = _web_hook_factory
        self.message_builder = message_builder

    def order_created(self, dto: OrderCreatedDTO):
        webhook = self._web_hook_factory(
            platform=dto.platform,
            category=dto.category
        )
        message = self.message_builder().execute(dto)
        webhook.send(message.content, username=BOT_NAME, embed=message.embed)
