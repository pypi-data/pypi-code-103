#  Copyright (c) 2020 Xavier Baró
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" Activity Report views module """
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets
from rest_framework import exceptions
from rest_framework.filters import OrderingFilter
from rest_framework.filters import SearchFilter
from rest_framework_extensions.mixins import DetailSerializerMixin
from rest_framework_extensions.mixins import NestedViewSetMixin

from tesla_ce.apps.api.v2.serializers import InstitutionCourseActivityReportExtendedSerializer
from tesla_ce.apps.api.v2.serializers import InstitutionCourseActivityReportSerializer
from tesla_ce.apps.api import permissions

from tesla_ce.models import Course
from tesla_ce.models import ReportActivity
from tesla_ce.models.user import get_institution_user
from tesla_ce.models.user import is_global_admin


# pylint: disable=too-many-ancestors
class InstitutionCourseActivityReportViewSet(NestedViewSetMixin, DetailSerializerMixin, viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows view activity reports.
    """
    model = ReportActivity
    queryset = ReportActivity.objects
    serializer_class = InstitutionCourseActivityReportSerializer
    serializer_detail_class = InstitutionCourseActivityReportExtendedSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['learner__first_name', 'learner__last_name', 'learner__email',
                     'identity_level', 'content_level', 'integrity_level']
    filterset_fields = ['learner__first_name', 'learner__last_name', 'learner__email',
                        'identity_level', 'content_level', 'integrity_level']
    permission_classes = [
        permissions.GlobalAdminReadOnlyPermission |
        permissions.InstitutionAdminReadOnlyPermission |
        permissions.InstitutionDataAdminReadOnlyPermission |
        permissions.InstitutionCourseInstructorReadOnlyPermission |
        permissions.InstitutionCourseLearnerReadOnlyPermission
    ]

    def get_queryset(self):
        queryset = self.filter_queryset_by_parents_lookups(ReportActivity.objects)
        if not is_global_admin(self.request.user):
            inst_user = get_institution_user(self.request.user)
            if not inst_user.inst_admin and not inst_user.legal_admin and not inst_user.data_admin:
                course = Course.objects.get(vle__institution=self.kwargs['parent_lookup_activity__vle__institution_id'],
                                            id=self.kwargs['parent_lookup_activity__course_id'])
                try:
                    is_instructor = self.request.user.instructor in course.instructors.all()
                except Exception:
                    is_instructor = False
                if not is_instructor:
                    if not inst_user.institution.allow_learner_report:
                        raise exceptions.PermissionDenied('Not allowed')
                    queryset = queryset.filter(learner_id=inst_user.id)
        return queryset.all()
