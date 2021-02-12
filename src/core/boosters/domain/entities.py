

class Booster:
    def __init__(
        self,
        _id: int,
        username: str,
        rating: float,
        avatar: str,
        user_id: int
    ):
        self.user_id = user_id
        self.avatar = avatar
        self.rating = rating
        self.username = username
        self.id = _id
