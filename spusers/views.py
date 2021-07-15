from rest_framework.response import Response
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import get_user_model

from spusers.serializers import UserSerializer, UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer, UserProfileUpdateSerializer
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_304_NOT_MODIFIED
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import FileUploadParser

from .models import User, Image
from spusers.settings import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH, LOCAL_OAUTH2_KEY, ADMIN_EMAILS
import requests as makerequest

from .permissions import IsAdmin

class RegisterView(APIView):
    """
    An API endpoint for user registration.
    POST must contain 'username', 'email', 'first_name', 'last_name' and 'password' fields.
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = UserRegisterSerializer(
            data=request.data, context={'request': request})

        # Return a 400 response if the data was invalid.
        serializer.is_valid()
        if not serializer.is_valid():
            if serializer.errors:
                error_message = ''
                error_field = ''
                email_val_error = serializer.errors.get('email')
                username_val_error = serializer.errors.get('username')
                password_val_error = serializer.errors.get('password')
                result = {'success': False, 'type': 'validation'}

                if email_val_error:
                    error_message = email_val_error[0]
                    error_field = 'email'
                    result['err_field'] = error_field
                    result['message'] = error_message
                    return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_400_BAD_REQUEST)
                
                if username_val_error:
                    error_message = username_val_error[0]
                    error_field = 'username'
                    result['err_field'] = error_field
                    result['message'] = error_message
                    return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_400_BAD_REQUEST)

                if password_val_error:
                    error_message = password_val_error[0]
                    error_field = 'password'
                    result['err_field'] = error_field
                    result['message'] = error_message
                    return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_400_BAD_REQUEST)

            # responseObj = { 'data': serializer.errors, 'success': False }
            # return HttpResponse(json.dumps(responseObj, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_400_BAD_REQUEST)


        validated_data = serializer.validated_data

        # need anothe way to handle this in future.
        is_admin = False
        if validated_data['email'] in ADMIN_EMAILS:
            is_admin = True

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            is_admin=is_admin
        )
        user.set_password(validated_data['password'])
        user.save()
        dataobj = {
            'data': serializer.data,
            'success': True
        }

        return HttpResponse(json.dumps(dataobj, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_201_CREATED)


class UserLoginAPIView(APIView):
    """
    Endpoint for user login. Returns authentication token on success.
    """

    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer
    user_class = get_user_model()


    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid()

        if not serializer.is_valid():
            result = {'success': False, 'type': 'login'}
            result['message'] = 'Login failed, Please check the credentials.'
            result['err_field'] = None
            return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_400_BAD_REQUEST)

        user = serializer.validated_data['user_obj']
        user_serializer = UserSerializer(user)
        print (user)

        data_obj = {
            'token': serializer.data['token'],
            'data': user_serializer.data,
            'success': True
            }
        return HttpResponse(json.dumps(data_obj, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_200_OK)


class UserProfileAPIView(generics.RetrieveAPIView):
    """
    Endpoint to retrieve user profile.
    """

    permission_classes = (IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )
    serializer_class = UserProfileSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user, context={'request': request})
        data_obj = {
            'data': serializer.data,
            'success': True
            }
        return HttpResponse(json.dumps(data_obj, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_200_OK)

class UserProfileUpdateAPIView(generics.RetrieveAPIView):
    """
    Endpoint to retrieve user profile.
    """

    permission_classes = (IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )
    serializer_class = UserProfileSerializer

    def post(self, request):
        serializer = UserProfileUpdateSerializer(
            data=request.data, context={'request': request})

        # Return a 400 response if the data was invalid.
        serializer.is_valid()
        if not serializer.is_valid():
            if serializer.errors:
                error_message = ''
                error_field = ''
        
                result = {'success': False, 'type': 'validation'}

                result['err_field'] = ''
                result['message'] = 'Error'

                return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_304_NOT_MODIFIED)

        validated_data = serializer.validated_data
        user = User.objects.get(unique_id=request.data['unique_id'])
        user.first_name = validated_data['first_name']
        user.last_name = validated_data['last_name']

        user.save()
        dataobj = {
            'data': serializer.data,
            'success': True
        }

        return HttpResponse(json.dumps(dataobj, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_200_OK)


class UserProfileImageUpdateAPIView(APIView):
    """
    Endpoint to retrieve user profile.
    """

    permission_classes = (IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )
    parser_class = (FileUploadParser,)


    def post(self, request):

        result = {'success': False, 'type': 'UnExpected', 'err_field': '', 'message': 'UnExpected Error'}
        image_data = None
        
        try:
        # print (images_data)try:
            image_data = request.data.get('file')
        except AttributeError as e:
            print (e)

        user = User.objects.get(unique_id=request.data['unique_id'])

        if not user:
            return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_304_NOT_MODIFIED)

        if not image_data:
            return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_304_NOT_MODIFIED)

        
        image = Image(user=user, image=image_data)
        image.save()

        data_to_send = {
            'image_id': image.uuid,
            'user_id': user.unique_id
        }

        dataobj = {
            'data': data_to_send,
            'success': True
        }

        return HttpResponse(json.dumps(dataobj, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_200_OK)


class UserListAPIView(APIView):
    """
    Endpoint for user list.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    authentication_classes = (TokenAuthentication, )
    serializer_class = UserProfileSerializer

    def get(self, request):
        queryset = User.objects.all()
        serializer = self.serializer_class(queryset, many=True)

        
        users = []
        for user_data in serializer.data:
            image = None
            user = User.objects.get(unique_id=user_data['unique_id'])
            try:
                image = Image.objects.filter(user=user).order_by('created').reverse()[0]
            except IndexError as e:
                pass

            image_obj = {}
            if image:
                image_obj['url'] = image.image.url
                image_obj['name'] = image.image.name
                image_obj['path'] = image.image.path
                image_obj['id'] = image.uuid

            user_obj = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'image': image_obj
            }

            users.append(user_obj)

        data_obj = {
            'data': users,
            'success': True
        }
        return HttpResponse(json.dumps(data_obj, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_200_OK)
