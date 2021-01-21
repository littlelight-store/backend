from enum import Enum


class OrderStatus(Enum):
    is_checking_payment = 'is_checking_payment'
    waiting_for_booster = 'waiting_for_booster'
    in_progress = 'in_progress'
    attempt_authorization = 'attempt_authorization'
    two_factor_code_required = 'two_factor_code_required'
    cant_sign_in = 'cant_sign_in'
    paused = 'paused'
    pending_approval = 'pending_approval'
    is_complete = 'is_complete'
    canceled = 'canceled'
