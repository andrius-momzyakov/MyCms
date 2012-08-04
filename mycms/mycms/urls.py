# coding:utf-8

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout

import cms.views
import settings

from cms.feed import LatestBlogEntriesFeed

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    #url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    #url(r'^static/images/(?P<path>.*)$', 'django.views.static.serve', \
    #              {'document_root': settings.STATIC_ROOT + '/images/'}),
    #url(r'^static/images_mini/(?P<path>.*)$', 'django.views.static.serve', \
    #              {'document_root': settings.STATIC_ROOT + '/images_mini/'}),
    #url(r'^static/js/(?P<path>.*)$', 'django.views.static.serve', \
    #              {'document_root': settings.STATIC_ROOT + '/js/'}),
    # Examples:
    # url(r'^$', 'mycms.views.home', name='home'),
    # url(r'^mycms/', include('mycms.foo.urls')),

    url(r'^content/(?P<section_code>.*)/', cms.views.dispatcher),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', cms.views.hi),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^now/', cms.views.getnow),
    #url(r'^timezones/', cms.views.list_tz),
    url(r'logout/', cms.views.my_logout),
    url(r'upload/', cms.views.upload_static_file),
    url(r'upload_ok/', cms.views.ok_message),
    url(r'^accounts/login/$',  login),
#    (r'^accounts/logout/$', logout),
    url(r'^accounts/logout/$', cms.views.my_logout),
    url(r'^result/(?P<name>.*)/$', cms.views.show_result),
    url(r'^send_message/$', cms.views.site_message_form),
    
    url(r'^rss/$', LatestBlogEntriesFeed()),

    url(r'^', cms.views.hi)
)

urlpatterns += staticfiles_urlpatterns()
