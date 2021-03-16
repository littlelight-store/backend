from core.application.dtos.notifications.event_notifications import EventChatMessageDTO, EventOrderCreatedDTO
from core.application.repositories.notifications import BoosterAssignedNotificationDTO

order_created_message = """☄️ Service: {service_title}
💰 Price: {total_price}

😎 User: ({username}): {user_email} 
🎮 Platform: {platform}
⚡️ Class: {character_class}
{promo_block}
"""

OPTIONS_TEMPLATE = """\n⚡️ {description} — ${price}"""


def get_new_order_message(dto: EventOrderCreatedDTO) -> str:

    promo_code = f"\n🔑 Promo Code: {dto.promo_code}"

    fmt = order_created_message.format(
        **dto.dict(exclude={'platform', 'character_class'}),
        platform=dto.platform.name,
        character_class=dto.character_class.name,
        promo_block=promo_code if dto.promo_code else ''
    )

    for o in dto.options:
        fmt += OPTIONS_TEMPLATE.format(
            description=o.description,
            price=o.price
        )

    return fmt


new_chat_message = """🤐
From: ({from_}) -> To: ({to_})
Text: {txt}
"""


def get_new_chat_message(dto: EventChatMessageDTO):
    fmt = new_chat_message.format(
        txt=dto.text,
        from_=dto.from_,
        to_=dto.to_
    )
    return fmt


booster_assigned_message = """🤖
Booster {booster_username} has took the order {order_id} ({order_service})
"""


def get_booster_assigned_message(dto: BoosterAssignedNotificationDTO):
    fmt = booster_assigned_message.format(
        booster_username=dto.booster_username,
        order_id=dto.order_id,
        order_service=dto.order_service
    )
    return fmt