from dependency_injector.wiring import Provide, inject
from django.http import JsonResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.clients.application.dashboard.list_client_dashboard_use_case import (
    ListClientDashboardUseCase,
    ListClientDashboardUseCaseDTOInput,
)
from core.clients.application.dashboard.set_membership_credentials_uc import (
    SetMembershipCredentialsDTOInput,
    SetMembershipCredentialsUseCase,
)
from infrastructure.injectors.application import ApplicationContainer
from infrastructure.web.service_api import fix_images_url


class ClientDashboardAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @inject
    def get(
        self,
        request,
        uc: ListClientDashboardUseCase = Provide[ApplicationContainer.client_dashboard_uc.list_client_dashboard_uc]
    ):
        dto = ListClientDashboardUseCaseDTOInput(
            client_id=request.user.id
        )
        res = uc.execute(dto)

        for item in res.orders:
            item.service_image = fix_images_url(request, item.service_image)

        return JsonResponse(data=res.dict(), status=200)

    def post(self, request):
        print(self, print(request))
        return Response(data=[str(request.user), 'posted'], status=200)


class ClientDashboardCredentialsAPI(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @inject
    def patch(
        self,
        request,
        uc: SetMembershipCredentialsUseCase = Provide[ApplicationContainer.client_dashboard_uc.set_membership_credentials_uc]
    ):
        dto = SetMembershipCredentialsDTOInput(
            client_id=request.user.id,
            credentials_name=request.data.get('credentials_name'),
            credentials_value=request.data.get('credentials_value'),
            platform=request.data.get('platform')
        )
        res = uc.execute(dto)

        return JsonResponse(data=res.dict(), status=200)