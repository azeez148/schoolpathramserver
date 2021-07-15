from .models import User
from rest_framework import serializers
from spusers import settings
from django.db.models import Q

from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('unique_id', 'username', 'email', 'first_name', 'last_name', 'phone_no', 'is_admin')


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    A serializer for registering users
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'is_admin')
        extra_kwargs = {
            'username': {'required': True, 'max_length': settings.USERNAME_MAX_LENGTH,
                         'min_length': settings.USERNAME_MIN_LENGTH},
            'email': {'required': True},
            'password': {'required': True, 'max_length': settings.PASSWORD_MAX_LENGTH,
                         'min_length': settings.PASSWORD_MIN_LENGTH},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


class UserLoginSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        write_only=True,
        label="Email Address"
    )

    token = serializers.CharField(
        allow_blank=True,
        read_only=True
    )

    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    class Meta(object):
        model = User
        fields = ['email', 'username', 'password', 'token', 'unique_id']

    def validate(self, data):
        result = {}
        email = data.get('email', None)
        username = data.get('username', None)
        password = data.get('password', None)

        if not email and not username:
            raise serializers.ValidationError("Please enter username or email to login.")

        user = User.objects.filter(
            Q(email=email) | Q(username=username)
        ).exclude(
            email__isnull=True
        ).exclude(
            email__iexact=''
        ).distinct()

        if user.exists() and user.count() == 1:
            user_obj = user.first()
        else:
            raise serializers.ValidationError("This username/email is not valid.")

        if user_obj:
            if not user_obj.check_password(password):
                raise serializers.ValidationError("Invalid credentials.")
            
            token, created = Token.objects.get_or_create(user=user_obj)
            result['token'] = token
            result['user_obj'] = user_obj

        # if user_obj.is_active:
        #     token, created = Token.objects.get_or_create(user=user_obj)
        #     data['token'] = token
        # else:
        #     raise serializers.ValidationError("User not active.")
        # print (result)
        # print ('2')
        return result


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('unique_id', 'username', 'email', 'first_name', 'last_name', 'phone_no',)


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('unique_id', 'first_name', 'last_name')
