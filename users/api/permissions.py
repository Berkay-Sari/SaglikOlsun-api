from rest_framework.permissions import BasePermission


class IsPatientUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_patient)


class IsDoctorUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_doctor)
