from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#from django.views.generic.simple import direct_to_template
#from django.views.generic.base import TemplateView
from django.conf import settings
from django.conf.urls.static import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
import main.urls

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'competitions.views.home', name='home'),
    # url(r'^competitions/', include('competitions.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    #url('^500a11352194.html$', direct_to_template, {'template': '500a11352194.html'}),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(main.urls))
    # Uncomment the next line to enable the admin:
)
urlpatterns += staticfiles_urlpatterns()
