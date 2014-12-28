from django.conf.urls import patterns, include, url
from django.contrib import admin
from response.views import show_image

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wechat_server.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

#    url(r'^admin/', include(admin.site.urls)),

    url(r'^response/weixin/$', 'response.views.weixin'),
    url(r'^images/(.+)/$',show_image),
)
