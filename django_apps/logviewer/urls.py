from django.conf.urls.defaults import *
import views

urlpatterns = patterns('',
    url(r'^messages/$', views.account_list, name='account_list'),
    url(r'^messages/(?P<protocol>\w+)/(?P<uid>[\w\d\@\.\s]+)/add/$', views.message_add, name='message_add'),
    url(r'^messages/(?P<protocol>\w+)/(?P<uid>[\w\d\@\.\s]+)/$', views.other_account_list, name='other_account_list'),
    url(r'^messages/(?P<protocol>\w+)/(?P<uid>[\w\d\@\.\s\-]+)/(?P<other_uid>[\w\d\@\.\s\-]+)/$', views.message_list, name='message_list'),
)