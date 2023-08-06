"""
Viewsets for Degreed
"""

from edx_rbac.mixins import PermissionRequiredMixin
from rest_framework import permissions, viewsets

from django.core.exceptions import PermissionDenied
from django.http import Http404

from enterprise.models import EnterpriseCustomerUser
from integrated_channels.degreed.models import DegreedEnterpriseCustomerConfiguration

from .serializers import DegreedConfigSerializer


class DegreedConfigurationViewSet(PermissionRequiredMixin, viewsets.ModelViewSet):
    serializer_class = DegreedConfigSerializer
    permission_classes = (permissions.IsAuthenticated,)
    permission_required = 'enterprise.can_access_admin_dashboard'

    def get_queryset(self):
        enterprise_customer_users = EnterpriseCustomerUser.objects.filter(user_id=self.request.user.id)
        if enterprise_customer_users:
            enterprise_customers_uuids = [str(enterprise_customer_user.enterprise_customer.uuid) for
                                          enterprise_customer_user in enterprise_customer_users]
            enterprise_customer_uuid = self.request.query_params.get('enterprise_customer')

            if enterprise_customer_uuid:
                if enterprise_customer_uuid in enterprise_customers_uuids:
                    return DegreedEnterpriseCustomerConfiguration.objects.filter(
                        enterprise_customer__uuid=enterprise_customer_uuid
                    )
                raise PermissionDenied()
            return DegreedEnterpriseCustomerConfiguration.objects.filter(
                enterprise_customer__uuid__in=enterprise_customers_uuids
            )
        raise Http404
