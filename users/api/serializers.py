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
        extra_kwargs = {'password': {'write_only': True}, 'password2': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password': 'Passwords must match.'})
        return data

    @staticmethod
    def validate_email(value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already in use.')
        return value

    def save(self, is_doctor=False, is_patient=False, **kwargs):
        user = User.objects.create_user(
            email=self.validated_data['email'],
            username=self.validated_data['username'],
            password=self.validated_data['password']
        )

        if is_doctor:
            Doctor.objects.create(user=user)
            user.is_doctor = True
        elif is_patient:
            Patient.objects.create(user=user)
            user.is_patient = True

        user.save()

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
