from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'main.views.main_page'),
    url(r'^cabinet(?:/(\d+)/)?$', 'main.views.view_order'),
    url(r'^results(?:/(\d+)/)?$', 'main.views.get_results'),
    url(r'^cabinet/school$', 'main.views.view_school'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login',
                        {'template_name' : 'login.html'}),
    (r'^accounts/logout/$', 'main.views.logout_view'),
    (r'^accounts/change_password/$',
     'django.contrib.auth.views.password_change', {
         'template_name': 'change_password.html',
     }),
    (r'^accounts/reset_password/$',
     'django.contrib.auth.views.password_reset', {
         'template_name': 'password_reset.html',
     }),
    (r'^accounts/reset_password_done/$',
     'django.contrib.auth.views.password_reset_done', {
         'template_name': 'password_reset_done.html',
     }),
    (r'^accounts/reset_password_confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
     'django.contrib.auth.views.password_reset_confirm',
     {
         'template_name': 'password_reset_confirm.html',
     }),
    (r'^accounts/reset_password_complete/$',
     'django.contrib.auth.views.password_reset_complete', {
         'template_name': 'password_reset_complete.html',
     }),

    (r'^accounts/change_password_done$',
     'django.contrib.auth.views.password_change_done',
     {'template_name': 'change_password_done.html'}),
    (r'^static/admin/jsi18n/',
                        'django.views.i18n.javascript_catalog'),

)

