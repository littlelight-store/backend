from . import cart_api
from . import client_dashboard_api
from . import service_api


def wire_api():
    from boosting import container
    container.wire(modules=[cart_api, client_dashboard_api, service_api])
