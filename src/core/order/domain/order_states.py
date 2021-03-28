from django.utils.timezone import now
from django_transitions.workflow import StateMachineMixinBase, StatusBase

from transitions import Machine


class OrderObjectiveStatusSM(StatusBase):
    """Workflow for Order objective status."""

    from core.order.domain.consts import OrderObjectiveStatus

    # Define the states as constants
    CREATED = OrderObjectiveStatus.CREATED
    PROCESSING = OrderObjectiveStatus.PROCESSING
    AWAITING_BOOSTER = OrderObjectiveStatus.AWAITING_BOOSTER
    TRYING_TO_LOGIN = OrderObjectiveStatus.TRYING_TO_LOGIN
    REQUIRED_2FA_CODE = OrderObjectiveStatus.REQUIRED_2FA_CODE
    INVALID_CREDENTIALS = OrderObjectiveStatus.INVALID_CREDENTIALS
    IN_PROGRESS = OrderObjectiveStatus.IN_PROGRESS
    PAUSED_BOOSTER = OrderObjectiveStatus.PAUSED_BOOSTER
    PAUSED_CONDITION = OrderObjectiveStatus.PAUSED_CONDITION
    PENDING_APPROVAL = OrderObjectiveStatus.PENDING_APPROVAL
    SET_REVIEW = OrderObjectiveStatus.SET_REVIEW
    DISRUPTED = OrderObjectiveStatus.DISRUPTED
    COMPLETED = OrderObjectiveStatus.COMPLETED

    # Give the states a human readable label
    STATE_CHOICES = (
        (CREATED.value, 'Order created'),
        (PROCESSING.value, 'In processing'),
        (AWAITING_BOOSTER.value, 'Awaiting for booster to sign in'),
        (TRYING_TO_LOGIN.value, 'Trying to login'),
        (REQUIRED_2FA_CODE.value, 'Required 2fa code'),
        (INVALID_CREDENTIALS.value, 'Invalid credentials set'),
        (IN_PROGRESS.value, 'In progress'),
        (PAUSED_BOOSTER.value, 'Paused booster'),
        (PAUSED_CONDITION.value, 'Paused condition'),
        (PENDING_APPROVAL.value, 'Pending approval'),
        (SET_REVIEW.value, 'Set review'),
        (DISRUPTED.value, 'Disrupted'),
        (COMPLETED.value, 'Completed'),
    )

    # Define the transitions as constants
    SET_PROCESSING = 'processing'
    SET_BOOSTER_ASSIGNED = 'booster_assigned'
    SET_BOOSTER_ACCEPTED = 'booster_accepted'
    SET_TRYING_TO_SIGN_IN = 'trying_to_sign_in'
    SET_REQUIRED_2FA_CODE = 'required_2fa_code'
    SET_INVALID_CREDENTIALS = 'invalid_credentials'
    SET_SIGNED_IN = 'signed_in'
    SET_PAUSE_BOOSTER = 'pause_booster'
    SET_PAUSE_CONDITION = 'pause_condition'
    SET_IN_PROGRESS = 'in_progress'
    SET_COMPLETED = 'completed'
    SET_PENDING_APPROVAL = 'pending_approval'

    # Give the transitions a human readable label and css class
    # which will be used in the django admin
    TRANSITION_LABELS = {
        SET_PROCESSING: {'label': 'Process current order', 'cssclass': 'default'},
        SET_BOOSTER_ASSIGNED: {'label': 'Set booster assigned', 'cssclass': 'default'},
        SET_TRYING_TO_SIGN_IN: {'label': 'Set trying to sign in'},
        SET_REQUIRED_2FA_CODE: {'label': 'Set required 2fa code'},
        SET_INVALID_CREDENTIALS: {'label': 'Set invalid credentials'},
        SET_SIGNED_IN: {'label': 'Set signed in'},
        SET_PAUSE_BOOSTER: {'label': 'Set pause booster'},
        SET_PAUSE_CONDITION: {'label': 'Set pause condition'},
        SET_IN_PROGRESS: {'label': 'Set in progress'},
        SET_COMPLETED: {'label': 'Set completed'},
        SET_PENDING_APPROVAL: {'label': 'Set pending approval'},
        SET_BOOSTER_ACCEPTED: {'label': 'Set booster accepted'}
    }

    # Construct the values to pass to the state machine constructor

    # The states of the machine
    SM_STATES = [
        CREATED,
        PROCESSING,
        AWAITING_BOOSTER,
        TRYING_TO_LOGIN,
        REQUIRED_2FA_CODE,
        INVALID_CREDENTIALS,
        IN_PROGRESS,
        PAUSED_BOOSTER,
        PAUSED_CONDITION,
        PENDING_APPROVAL,
        SET_REVIEW,
        DISRUPTED,
        COMPLETED
    ]

    # The machines initial state
    SM_INITIAL_STATE = CREATED

    # The transititions as a list of dictionaries
    SM_TRANSITIONS = [
        {
            'trigger': SET_BOOSTER_ACCEPTED,
            'source': '*',
            'dest': TRYING_TO_LOGIN,
        },

        # trigger, source, destination
        {
            'trigger': SET_PROCESSING,
            'source': '*',
            'dest': PROCESSING,
        },

        {
            'trigger': SET_BOOSTER_ASSIGNED,
            'source': '*',
            'dest': AWAITING_BOOSTER,
        },

        {
            'trigger': SET_TRYING_TO_SIGN_IN,
            'source': '*',
            'dest': TRYING_TO_LOGIN,
        },

        {
            'trigger': SET_PAUSE_BOOSTER,
            'source': '*',
            'dest': PAUSED_BOOSTER,
            'after': 'task_order_paused'
        },

        {
            'trigger': SET_IN_PROGRESS,
            'source': '*',
            'dest': IN_PROGRESS,
        },

        # Branch of unsuccess auth
        {
            'trigger': SET_INVALID_CREDENTIALS,
            'source': '*',
            'dest': INVALID_CREDENTIALS,
            'after': 'task_invalid_credentials'
        },
        {
            'trigger': SET_REQUIRED_2FA_CODE,
            'source': '*',
            'dest': REQUIRED_2FA_CODE,
            'after': 'task_2fa_required'
        },


        # Client must check result
        {
            'trigger': SET_PENDING_APPROVAL,
            'source': '*',
            'dest': PENDING_APPROVAL,
            'after': 'task_pending_approval'
        },
        {
            'trigger': SET_COMPLETED,
            'source': PENDING_APPROVAL,
            'dest': COMPLETED
        }
    ]


def get_state_machine(notifier):
    m = Machine(
        notifier,
        **OrderObjectiveStatusSM.get_kwargs()  # noqa: C815
    )
    return m


class OrderObjectiveStateMachineMixin(StateMachineMixinBase):
    """Lifecycle workflow state machine."""

    status_class = OrderObjectiveStatusSM

    machine = Machine(
        model=None,
        auto_transitions=False,
        after_state_change='status_updated',
        **status_class.get_kwargs()  # noqa: C815
    )

    @property
    def state(self):
        """Get the items workflowstate or the initial state if none is set."""
        if self.status:
            return self.status
        return self.machine.initial

    @state.setter
    def state(self, value):
        """Set the items workflow state."""
        self.status = value
        return self.status

    def status_updated(self):
        self.status_changed_at = now()

    def task_pending_approval(self):
        from orders.tasks import set_pending_approval_task
        set_pending_approval_task.delay(order_objective_id=self.id)

    def task_order_paused(self):
        from orders.tasks import set_paused_task
        set_paused_task.delay(order_objective_id=self.id, client_id=self.client_id)

    def task_2fa_required(self):
        from orders.tasks import required_2fa_code_task
        required_2fa_code_task.delay(client_id=self.client_id)

    def task_invalid_credentials(self):
        from orders.tasks import invalid_credentials_task
        invalid_credentials_task.delay(client_id=self.client_id, order_objective_id=self.id)
