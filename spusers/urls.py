from django.conf.urls import url, include
from spusers import views

urlpatterns = [
    # url(r'^account/password/', views.AccountPasswordView.as_view()),
    # url(r'^account/social/', views.AccountSocialView.as_view()),
    url(r'^profile/', views.UserProfileAPIView.as_view()),
    # url(r'^register/check-email/', views.RegisterCheckEmailView.as_view()),
    # url(r'^register/check-username/', views.RegisterCheckUsernameView.as_view()),
    url(r'^register/', views.RegisterView.as_view()),
    url(r'^update-profile/', views.UserProfileUpdateAPIView.as_view()),
    url(r'^update-profile-image/', views.UserProfileImageUpdateAPIView.as_view()),

    
    # url(r'^social-auth/google-auth-code/', views.GoogleAuthCodeView.as_view()),
    # url(r'^social-auth/', include('rest_framework_social_oauth2.urls')),
    # url(r'^oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^list-users/', views.UserListAPIView.as_view()),
    url(r'^login/$',
        views.UserLoginAPIView.as_view(),
        name='login'),
]
