from django.shortcuts import render
from rest_auth.registration.views import RegisterView
from rest_auth.views import LoginView
from rest_framework.response import Response
from rest_framework import status


from .serializers import GecoRegisterSerializer
from .models import GecoUser
# Create your views here.

class GecoRegisterView(RegisterView):

    serializer_class = GecoRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        
        geco_user = GecoUser.objects.get(user=user)
        user_dir = geco_user.user_dir

        headers = self.get_success_headers(serializer.data)

        response = self.get_response_data(user)
        response['user_dir'] = user_dir
        return Response(response,
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class GecoLoginView(LoginView):

    def get_response(self):
        serializer_class = self.get_response_serializer()


       
        serializer = serializer_class(instance=self.token,
                                        context={'request': self.request})
        geco_user = GecoUser.objects.get(user=self.user)
        user_dir = geco_user.user_dir

        res_data = {k:v for k,v in  serializer.data.items()}
        res_data['user_dir'] = user_dir
        response = Response(res_data, status=status.HTTP_200_OK)
        
        return response