from django.urls import path
from .views import (DoctorSignUpView, PatientSignUpView, CustomAuthToken, LogoutView, DoctorOnlyView, PatientOnlyView,
                    AddDoctorToPatientView, ListDoctorsOfPatientView, ListPatientsOfDoctorView, UpdateDoctorDataView,
                    UpdatePatientDataView, IsPatientView, PredictHeartDiseaseView)

urlpatterns = [
    path('signup/doctor', DoctorSignUpView.as_view(), name='doctor_signup'),
    path('signup/patient', PatientSignUpView.as_view(), name='patient_signup'),
    path('login/', CustomAuthToken.as_view(), name='auth_token'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('doctor/dashboard/', DoctorOnlyView.as_view(), name='doctor_dashboard'),
    path('patient/dashboard/', PatientOnlyView.as_view(), name='patient_dashboard'),
    path('patient/add-doctor/', AddDoctorToPatientView.as_view(), name='add_doctor_to_patient'),
    path('patient/list-doctors/', ListDoctorsOfPatientView.as_view(), name='list_doctors_of_patient'),
    path('doctor/list-patients/', ListPatientsOfDoctorView.as_view(), name='list_patients_of_doctor'),
    path('doctor/update', UpdateDoctorDataView.as_view(), name='update_doctor'),
    path('patient/update', UpdatePatientDataView.as_view(), name='update_patient'),
    path('is-patient/', IsPatientView.as_view(), name='is_patient'),
    path('predict-heart-disease/', PredictHeartDiseaseView.as_view(), name='predict_heart_disease'),
]
