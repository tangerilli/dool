from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    url(r'^messages/$', views.account_list, name='account_list'),
    url(r'^messages/(?P<protocol>\w+)/(?P<uid>[\w\d\@\.\s\-\/]+)/add/$', views.message_add, name='message_add'),
    url(r'^messages/(?P<protocol>\w+)/(?P<uid>[\w\d\@\.\s]+)/$', views.other_account_list, name='other_account_list'),
    url(r'^messages/(?P<protocol>\w+)/(?P<uid>[\w\d\@\.\s\-\/]+)/(?P<other_uid>[\w\d\@\.\s\-\/]+)/$', views.message_list, name='message_list'),
    url(r'^search/$', views.search, name='search'),
    url(r'^search/(?P<protocol>\w+)/(?P<uid>[\w\d\@\.\s\-]+)/$', views.search, name='search'),
    url(r'^search/(?P<protocol>\w+)/(?P<uid>[\w\d\@\.\s\-\/]+)/(?P<other_uid>[\w\d\@\.\s\-\/]+)/$', views.search, name='search'),
)