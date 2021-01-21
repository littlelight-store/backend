from core.domain.object_values import BoosterId, UserId


class Booster:
    def __init__(
        self,
        _id: BoosterId,
        user_id: UserId,
        discord_id: str,
        username: str
    ):
        self.id = _id
        self.discord_id = discord_id
        self.user_id = user_id
        self.username = username
