from rest_framework.response import Response
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
import json
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import get_user_model
from django.http import QueryDict

from spnewsfeed.serializers import NewsFeedSerializer
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_304_NOT_MODIFIED
from rest_framework.permissions import AllowAny, IsAuthenticated

from spusers.models import User
from spusers.settings import PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH, LOCAL_OAUTH2_KEY
import requests as makerequest

from spusers.permissions import IsAdmin


from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser


from .models import NewsFeed, Image


class NewsFeedView(APIView):
    """
    An API endpoint for user registration.
    POST must contain 'username', 'email', 'first_name', 'last_name' and 'password' fields.
    """
    permission_classes = [IsAuthenticated, IsAdmin]
    authentication_classes = (TokenAuthentication, )
    # parser_classes = (MultiPartParser, FormParser,)
    parser_class = (FileUploadParser,)



    def post(self, request):

        # newsfeed_obj = NewsFeed(title=request.data['title'], description=request.data['description'], is_active=True, created_by=user)
        # newsfeed_obj_dict = newsfeed_obj.__dict__

        # print (request.data)
        images_data = []
        try:
            images_data = request.data.pop('file')
        except AttributeError as e:
            print (e)

        # print (images_data)


        user = User.objects.get(unique_id=request.data['created_by'])

        ordinary_dict = {'created_by': user.id, 'title': request.data['title'],  'description': request.data['description'] }
        query_dict = QueryDict('', mutable=True)
        query_dict.update(ordinary_dict)
        

        # print (newsfeed_obj_dict)
        serializer = NewsFeedSerializer(
            data=query_dict, context={'request': request})

        # Return a 400 response if the data was invalid.
        serializer.is_valid()
        if not serializer.is_valid():
            if serializer.errors:
                error_message = ''
                error_field = ''
                # email_val_error = serializer.errors.get('email')
                # username_val_error = serializer.errors.get('username')
                # password_val_error = serializer.errors.get('password')
                # result = {'success': False, 'type': 'validation'}

                # if email_val_error:
                #     error_message = email_val_error[0]
                #     error_field = 'email'
                #     result['err_field'] = error_field
                #     result['message'] = error_message
                #     return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_400_BAD_REQUEST)
                
                # if username_val_error:
                #     error_message = username_val_error[0]
                #     error_field = 'username'
                #     result['err_field'] = error_field
                #     result['message'] = error_message
                #     return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_400_BAD_REQUEST)

                # if password_val_error:
                #     error_message = password_val_error[0]
                #     error_field = 'password'
                #     result['err_field'] = error_field
                #     result['message'] = error_message
                #     return HttpResponse(json.dumps(result, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_400_BAD_REQUEST)

            responseObj = { 'data': serializer.errors, 'success': False }
            return HttpResponse(json.dumps(responseObj, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        print (validated_data)

        newsfeed = NewsFeed.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            is_active=True,
            created_by=validated_data['created_by']
        )

        newsfeed.save()
        image_data_list = []

        try:
            for image_data in images_data:
                image = Image(newsfeed=newsfeed, image=image_data)
                image.save()
                image_data_list.append(str(image))
            else:
                print ('test')
        except Exception as inst:
              print("An exception occurred")
              print (inst)

        newsfeedObj = {
            "title": newsfeed.title,
            "description": newsfeed.description,
            "created_by": newsfeed.created_by.first_name,
            "is_active": newsfeed.is_active,
            "images": image_data_list
        }
        dataobj = {
            'data': newsfeedObj,
            'success': True
        }

        return HttpResponse(json.dumps(dataobj, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_201_CREATED)

class NewsFeedListView(APIView):
    """
    Endpoint for user list.
    """
    permission_classes = (IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )
    serializer_class = NewsFeedSerializer

    def get(self, request):
        queryset = NewsFeed.objects.order_by('created').all().reverse()
        serializer = self.serializer_class(queryset, many=True)

        # import pudb; pudb.set_trace()
        newsfeed_list = []
        for newsfeed in serializer.data:
            user = User.objects.get(id=newsfeed['created_by'])
            image_list = []
            newsfeed_obj = NewsFeed.objects.get(uuid=newsfeed['uuid'])
            images = Image.objects.all().filter(newsfeed=newsfeed_obj)
            for image in images:
                image_obj = {}

                print (image.image.url)
                image_obj['url'] = image.image.url
                image_obj['name'] = image.image.name
                image_obj['path'] = image.image.path
                image_obj['id'] = image.uuid

                image_list.append(image_obj)

            newsfeedObj = {
                "title": newsfeed['title'],
                "description": newsfeed['description'],
                "created_by": user.first_name,
                "is_active": newsfeed['is_active'],
                "id": newsfeed['uuid'],
                "images": image_list
            }
            newsfeed_list.append(newsfeedObj)

        data_obj = {
            'data': newsfeed_list,
            'success': True
        }
        return HttpResponse(json.dumps(data_obj, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_200_OK)


class UpdateNewsFeedView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    authentication_classes = (TokenAuthentication, )
    serializer_class = NewsFeedSerializer

    def put(self, request, *args, **kwargs):
        images_data = []
        try:
            images_data = request.data.pop('file')
            print (images_data)

        except AttributeError as e:
            print (e)

        try:
            newsfeed = NewsFeed.objects.get(uuid=request.data['newsfeed_id'])
        except Exception as e:
            dataobj = {
            'data': str(e),
            'success': False
            }

            return HttpResponse(json.dumps(dataobj, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_304_NOT_MODIFIED)

        newsfeed.title = request.data['title']
        newsfeed.description = request.data['description']
        newsfeed.save()

        image_data_list = []

        # images = Image.objects.all().filter(newsfeed=newsfeed)
        # for image in images:
        #     image.delete()

        try:
            for image_data in images_data:
                image = Image(newsfeed=newsfeed, image=image_data)
                image.save()
                image_data_list.append(str(image))
            else:
                print ('test')
        except Exception as inst:
              print("An exception occurred")
              print (inst)

        newsfeedObj = {
            "title": newsfeed.title,
            "description": newsfeed.description,
            "created_by": newsfeed.created_by.first_name,
            "is_active": newsfeed.is_active,
            "images": image_data_list
        }


        dataobj = {
            'data': newsfeedObj,
            'success': True
        }

        return HttpResponse(json.dumps(dataobj, cls=DjangoJSONEncoder), content_type='application/json', status=HTTP_200_OK)

