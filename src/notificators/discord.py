import datetime as dt

from discord import Colour, Embed, RequestsWebhookAdapter, Webhook
from pydantic import BaseModel

from boosting.settings import BASE_URL
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


def get_dashboard_accept_order_link(order_id):
    return f"{BASE_URL}/dashboard?action=bind-order&param={order_id}"


class NewMessageBuilder:
    def _create_embed(self, dto: OrderCreatedDTO):
        embed = Embed(
            title=f'[{dto.order_id}] *{dto.service_title}*',
            colour=Colour.green(),
            timestamp=dt.datetime.utcnow(),
        )

        for service in dto.selected_services:
            embed.add_field(name='🚩', value=f"{service.description} — ${service.price}", inline=True)

        embed.add_field(name='👤 Client: ', value=f'*{dto.client_username}*', inline=False)
        embed.add_field(name='💰 You will get: ', value=f'*${dto.booster_price}*', inline=False)
        embed.add_field(
            name="🐲 Follow link to accept an order: (Must be authorized)",
            value=get_dashboard_accept_order_link(dto.order_id)
        )

        # embed.add_field(name='Add any reaction to accept an order', value=f'😉', inline=False)

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


class NewDiscordNotificator(OrderExecutorsNotificationRepository):
    def __init__(
        self,
        message_builder: type(NewMessageBuilder) = NewMessageBuilder,
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
