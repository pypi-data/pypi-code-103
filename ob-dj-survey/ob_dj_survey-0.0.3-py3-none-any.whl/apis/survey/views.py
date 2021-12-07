import logging

from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response

from ob_dj_survey.apis.survey.serializers import (
    SurveyAnswersSerializer,
    SurveySerializer,
)
from ob_dj_survey.core.survey.models import Survey, SurveyAnswers

logger = logging.getLogger(__name__)


class SurveyView(viewsets.ModelViewSet):
    model = Survey
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SurveySerializer

    def get_queryset(self):
        return Survey.objects.active()


class SurveyAnswersView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SurveyAnswersSerializer

    def get_queryset(self):
        return SurveyAnswers.objects.all()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
