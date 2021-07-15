from django.conf.urls import url, include
from spnewsfeed import views

urlpatterns = [
    # url(r'^account/password/', views.AccountPasswordView.as_view()),
    # url(r'^account/social/', views.AccountSocialView.as_view()),
    url(r'^delete/', views.NewsFeedView.as_view()),
    # url(r'^register/check-email/', views.RegisterCheckEmailView.as_view()),
    # url(r'^register/check-username/', views.RegisterCheckUsernameView.as_view()),
    url(r'^create/', views.NewsFeedView.as_view()),
    # url(r'^social-auth/google-auth-code/', views.GoogleAuthCodeView.as_view()),
    # url(r'^social-auth/', include('rest_framework_social_oauth2.urls')),
    # url(r'^oauth2/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^list-newsfeed/', views.NewsFeedListView.as_view()),
    url(r'^update-newsfeed/',
        views.UpdateNewsFeedView.as_view(),
        name='update'),
]
