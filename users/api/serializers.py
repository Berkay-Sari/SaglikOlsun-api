from rest_framework import serializers
from users.models import User, Patient, Doctor


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_patient']


class BaseSignUpSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}}

    def save(self, is_doctor=False, is_patient=False, **kwargs):
        user = User(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        user.set_password(password)
        user.save()

        if is_doctor:
            Doctor.objects.create(user=user)
        elif is_patient:
            Patient.objects.create(user=user)

        return user


class DoctorSignUpSerializer(BaseSignUpSerializer):
    class Meta(BaseSignUpSerializer.Meta):
        fields = BaseSignUpSerializer.Meta.fields + ['is_doctor']

    def save(self, **kwargs):
        return super().save(is_doctor=True, **kwargs)


class PatientSignUpSerializer(BaseSignUpSerializer):
    class Meta(BaseSignUpSerializer.Meta):
        fields = BaseSignUpSerializer.Meta.fields + ['is_patient']

    def save(self, **kwargs):
        return super().save(is_patient=True, **kwargs)
