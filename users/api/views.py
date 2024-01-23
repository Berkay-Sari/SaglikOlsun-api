from rest_framework import generics, status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken

from .permissions import IsDoctorUser, IsPatientUser
from .serializers import UserSerializer, DoctorSignUpSerializer, PatientSignUpSerializer


class DoctorSignUpView(generics.CreateAPIView):
    serializer_class = DoctorSignUpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        doctor = serializer.save()
        return Response({
            "user": UserSerializer(doctor, context=self.get_serializer_context()).data,
            "token": Token.objects.get(user=doctor).key,
            "message": "Doctor Created Successfully.  Now perform Login to get your token",
        })


class PatientSignUpView(generics.CreateAPIView):
    serializer_class = PatientSignUpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        patient = serializer.save()
        return Response({
            "patient": UserSerializer(patient, context=self.get_serializer_context()).data,
            "token": Token.objects.get(user=patient).key,
            "message": "Patient Created Successfully.  Now perform Login to get your token",
        })


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'is_patient': user.is_patient,
            'is_doctor': user.is_doctor,
        })


class LogoutView(APIView):
    @staticmethod
    def post(self, request):
        request.auth.delete()
        return Response(status=status.HTTP_200_OK)


class PatientOnlyView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated & IsPatientUser]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class DoctorOnlyView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated & IsDoctorUser]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
