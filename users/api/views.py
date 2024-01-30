from rest_framework import generics, status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken

from .permissions import IsDoctorUser, IsPatientUser
from .serializers import (UserSerializer, DoctorSerializer, PatientSerializer, DoctorSignUpSerializer,
                          PatientSignUpSerializer)
from ..models import Doctor


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
    def post(self, request):
        request.auth.delete()
        return Response(status=status.HTTP_200_OK)


class PatientOnlyView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated & IsPatientUser]
    serializer_class = PatientSerializer

    def get_object(self):
        return self.request.user.patient


class DoctorOnlyView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated & IsDoctorUser]
    serializer_class = DoctorSerializer

    def get_object(self):
        return self.request.user.doctor


class AddDoctorToPatientView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated & IsPatientUser]
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
    permission_classes = [permissions.IsAuthenticated & IsPatientUser]
    serializer_class = DoctorSerializer

    def get_queryset(self):
        return self.request.user.patient.doctors.all()


class ListPatientsOfDoctorView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated & IsDoctorUser]
    serializer_class = PatientSerializer

    def get_queryset(self):
        return self.request.user.doctor.patients.all()


class UpdateDoctorDataView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated & IsDoctorUser]
    serializer_class = DoctorSerializer

    def get_object(self):
        return self.request.user.doctor

    def update(self, request, *args, **kwargs):
        doctor = self.get_object()
        fields_to_update = ['birth_date', 'gender', 'speciality', 'background', 'start_date']

        for field in fields_to_update:
            if field in request.data:
                print(field)
                if hasattr(doctor.user, field):
                    setattr(doctor.user, field, request.data[field])
                else:
                    setattr(doctor, field, request.data[field])

        doctor.user.save()
        doctor.save()

        return Response({
            "message": f"Doctor '{doctor}' updated successfully.",
            "doctor_id": doctor.pk,
            "details": DoctorSerializer(doctor).data,
        }, status=status.HTTP_200_OK)


class UpdatePatientDataView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated & IsPatientUser]
    serializer_class = PatientSerializer

    def get_object(self):
        return self.request.user.patient

    def update(self, request, *args, **kwargs):
        patient = self.get_object()
        fields_to_update = ['birth_date', 'gender', 'height', 'weight', 'blood_type', 'allergies', 'medications',
                            'emergency_contact']

        for field in fields_to_update:
            if field in request.data:
                if hasattr(patient.user, field):
                    setattr(patient.user, field, request.data[field])
                else:
                    setattr(patient, field, request.data[field])

        patient.user.save()
        patient.save()

        return Response({
            "message": f"Patient '{patient}' updated successfully.",
            "patient_id": patient.pk,
            "details": PatientSerializer(patient).data,
        }, status=status.HTTP_200_OK)
