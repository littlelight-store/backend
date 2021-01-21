import enum


class OrderObjectiveStatus(str, enum.Enum):
    CREATED = 'CREATED'
    PROCESSING = 'PROCESSING'
    AWAITING_BOOSTER = 'AWAITING_BOOSTER'
    TRYING_TO_LOGIN = 'TRYING_TO_LOGIN'
    REQUIRED_2FA_CODE = 'REQUIRED_2FA_CODE'
    INVALID_CREDENTIALS = 'INVALID_CREDENTIALS'
    IN_PROGRESS = 'IN_PROGRESS'
    PAUSED_BOOSTER = 'PAUSED_BOOSTER'
    PAUSED_CONDITION = 'PAUSED_CONDITION'
    PENDING_APPROVAL = 'PENDING_APPROVAL'
    SET_REVIEW = 'SET_REVIEW'
    DISRUPTED = 'DISRUPTED'
    COMPLETED = 'COMPLETED'

    @classmethod
    def choices(cls):
        return tuple((i.name, i.value) for i in cls)
