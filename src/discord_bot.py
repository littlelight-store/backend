import sys
import logging
import os
import typing as t
import re
import discord
import django
from discord import Colour, Message, Member

from boosting.settings import DISCORD_BOT_TOKEN

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boosting.settings')
django.setup()

from core.application.use_cases.assign_booster_to_order import AssignBoosterToOrderUseCase
from core.domain.exceptions import OrderNotExists, BoosterNotExists
from orders.services import AssignBoosterService


logger = logging.getLogger()

client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


def get_order_id(title: str) -> int:
    match = re.match(r'^.*?\[[^\d]*(\d+)[^\d]*\].*$', title)
    return int(match.group(1))


@client.event
async def on_message(message: Message):
    if message.author == client.user:
        return

    embed = message.embeds[0]

    order_id = get_order_id(embed.title)

    if embed and embed.colour != Colour.red:
        reaction, user = await client.wait_for('reaction_add')  # type: t.Any, Member
        uc: AssignBoosterToOrderUseCase = AssignBoosterService.use_case()

        try:
            await uc.set_params(order_id, str(user)).execute()
        except (OrderNotExists, BoosterNotExists):
            logger.exception('Cannot assign order from discord')
        else:
            new_embed = embed
            new_embed.colour = Colour.red()
            new_embed.add_field(name=f'⚡️ Winner is', value=f'<@{user.id}>', inline=False)

            await message.channel.send(message.content, embed=new_embed)

logger.info("Discord bot is started")

client.run(DISCORD_BOT_TOKEN)
