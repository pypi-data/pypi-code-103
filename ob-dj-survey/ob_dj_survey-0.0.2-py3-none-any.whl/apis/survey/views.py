import logging

from rest_framework import permissions, viewsets

from ob_dj_survey.apis.survey.serializers import SurveySerializer
from ob_dj_survey.core.survey.models import Survey

logger = logging.getLogger(__name__)


class SurveyView(viewsets.ModelViewSet):
    model = Survey
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SurveySerializer

    def get_queryset(self):
        return Survey.objects.all()
