

class Booster:
    def __init__(
        self,
        _id: int,
        username: str,
        rating: float,
        avatar: str
    ):
        self.avatar = avatar
        self.rating = rating
        self.username = username
        self.id = _id
