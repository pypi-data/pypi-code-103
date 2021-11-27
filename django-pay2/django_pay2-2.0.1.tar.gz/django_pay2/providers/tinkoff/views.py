import logging

from rest_framework import renderers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import NotifySerializer

logger = logging.getLogger(__file__)


class NotifyView(APIView):
    renderer_classes = (renderers.StaticHTMLRenderer,)

    def post(self, request, *args, **kwargs):
        serializer = NotifySerializer(
            data=request.data, context={"raw_data": request.data}
        )
        if not serializer.is_valid():
            logger.warning(
                f"Tinkoff notification error: {serializer.errors}, orig data: {request.data}"
            )
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.validated_data["payment"].accept()
        return Response("OK")
