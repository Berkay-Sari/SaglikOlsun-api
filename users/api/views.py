from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsDoctorUser, IsPatientUser
from .serializers import (UserSerializer, DoctorSerializer, PatientSerializer, DoctorSignUpSerializer,
                          PatientSignUpSerializer)
from ..models import Doctor, Patient


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
    # noinspection PyMethodMayBeStatic
    def post(self, request):
        request.auth.delete()
        return Response(status=status.HTTP_200_OK)


class PatientOnlyView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated & IsPatientUser]
    serializer_class = PatientSerializer

    def get_object(self):
        return self.request.user.patient


class DoctorOnlyView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated & IsDoctorUser]
    serializer_class = DoctorSerializer

    def get_object(self):
        return self.request.user.doctor


class AddDoctorToPatientView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated & IsPatientUser]
    serializer_class = PatientSerializer

    def get_object(self):
        return self.request.user.patient

    def update(self, request, *args, **kwargs):
        patient = self.get_object()
        doctor_username = request.data.get('doctor_username')

        doctor = get_object_or_404(Doctor, user__username=doctor_username)

        patient.doctors.add(doctor)
        doctor.patients.add(patient)

        return Response({
            "message": f"Doctor '{doctor.user.username}' added to patient '{patient.user.username}' successfully.",
            "doctor_id": doctor.pk,
            "patient_id": patient.pk,
        }, status=status.HTTP_200_OK)


class ListDoctorsOfPatientView(generics.ListAPIView):
    permission_classes = [IsAuthenticated & IsPatientUser]
    serializer_class = DoctorSerializer

    def get_queryset(self):
        return self.request.user.patient.doctors.all()


class ListPatientsOfDoctorView(generics.ListAPIView):
    permission_classes = [IsAuthenticated & IsDoctorUser]
    serializer_class = PatientSerializer

    def get_queryset(self):
        return self.request.user.doctor.patients.all()


class UpdateUserDataView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        raise NotImplementedError("Subclasses must implement this method.")

    def update(self, request, *args, **kwargs):
        user_data = self.get_object()
        common_fields = ['first_name', 'last_name', 'birth_date', 'gender']
        sub_fields = [field.name for field in user_data._meta.get_fields()]
        fields_to_update = common_fields + sub_fields

        for field in fields_to_update:
            if field in request.data:
                if hasattr(user_data.user, field):
                    setattr(user_data.user, field, request.data[field])
                else:
                    setattr(user_data, field, request.data[field])

        user_data.user.save()
        user_data.save()

        return self.get_response(user_data)

    def get_response(self, user_data):
        raise NotImplementedError("Subclasses must implement this method.")


class UpdateDoctorDataView(UpdateUserDataView):
    permission_classes = [IsAuthenticated & IsDoctorUser]
    serializer_class = DoctorSerializer

    def get_object(self):
        return self.request.user.doctor

    def get_response(self, doctor):
        return Response({
            "message": f"Doctor '{doctor}' updated successfully.",
            "doctor_id": doctor.pk,
            "details": DoctorSerializer(doctor).data,
        }, status=status.HTTP_200_OK)


class UpdatePatientDataView(UpdateUserDataView):
    permission_classes = [IsAuthenticated & IsPatientUser]
    serializer_class = PatientSerializer

    def get_object(self):
        return self.request.user.patient

    def get_response(self, patient):
        return Response({
            "message": f"Patient '{patient}' updated successfully.",
            "patient_id": patient.pk,
            "details": PatientSerializer(patient).data,
        }, status=status.HTTP_200_OK)


class IsPatientView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "is_patient": request.user.is_patient,
        })
