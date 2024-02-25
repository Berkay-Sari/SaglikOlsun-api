from rest_framework import serializers
from users.models import User, Patient, Doctor, EmergencyContact


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'birth_date', 'gender', 'is_patient', 'is_doctor']


class BasicUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = ['username', 'email', 'birth_date', 'gender']


class DoctorSerializer(serializers.ModelSerializer):
    user = BasicUserSerializer()

    class Meta:
        model = Doctor
        fields = '__all__'


class PatientSerializer(serializers.ModelSerializer):
    user = BasicUserSerializer()

    class Meta:
        model = Patient
        fields = '__all__'


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

    # noinspection PyMethodMayBeStatic
    def validate_email(self, value):
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


class EmergencyContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyContact
        fields = '__all__'

    def create(self, validated_data):
        return EmergencyContact.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.relationship = validated_data.get('relationship', instance.relationship)
        instance.save()
        return instance
