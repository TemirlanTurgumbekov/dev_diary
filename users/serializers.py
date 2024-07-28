from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'password2', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        password = attrs['password']
        if password != attrs['password2']:
            raise serializers.ValidationError({"password": "Password didn't match"})
        
        if len(password) < 8:
            raise ValidationError(
                _("This password is too short. It must contain at least 8 characters."),
                code='password_too_short',
            )
        if not re.findall('\d', password):
            raise ValidationError(
                _("This password must contain at least one digit."),
                code='password_no_digit',
            )
        if not re.findall('[A-Z]', password) and not re.findall('[a-z]', password):
            raise ValidationError(
                _("This password must contain at least one letter."),
                code='password_no_letter',
            )

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = get_user_model().objects.create_user(**validated_data)
        return user
    

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('password', 'password2', 'email', 'role')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password didn't match"})
        return attrs
    
    def password_validator(password):
        if len(password) < 8:
            raise ValidationError(
                _("This password is too short. It must contain at least 8 characters."),
                code='password_too_short',
            )
        if not re.findall('\d', password):
            raise ValidationError(
                _("This password must contain at least one digit."),
                code='password_no_digit',
            )
        if not re.findall('[A-Z]', password) and not re.findall('[a-z]', password):
            raise ValidationError(
                _("This password must contain at least one letter."),
                code='password_no_letter',
            )

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            role=validated_data['role']
        )

        validate_password(validated_data['password'])
        user.set_password(validated_data['password'])
        user.save()
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = CustomUserSerializer(self.user).data
        return data