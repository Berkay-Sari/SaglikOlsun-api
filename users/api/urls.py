from django.urls import path
from .views import DoctorSignUpView, PatientSignUpView, CustomAuthToken, LogoutView, DoctorOnlyView, PatientOnlyView

urlpatterns = [
    path('signup/doctor', DoctorSignUpView.as_view(), name='doctor_signup'),
    path('signup/patient', PatientSignUpView.as_view(), name='patient_signup'),
    path('login/', CustomAuthToken.as_view(), name='auth_token'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('doctor/dashboard/', DoctorOnlyView.as_view(), name='doctor_dashboard'),
    path('patient/dashboard/', PatientOnlyView.as_view(), name='patient_dashboard')
]
