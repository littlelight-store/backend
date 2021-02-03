from infrastructure.web import cart_api
from infrastructure.web import client_dashboard_api, booster_dashboard_api
from infrastructure.web import service_api


def wire_api():
    from boosting import container
    container.wire(modules=[cart_api, client_dashboard_api, service_api, booster_dashboard_api])
