from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'app.views.home'),
	url(r'^checkin$', 'app.views.checkin'),
	url(r'^profile/view/(?P<iduser>\d+)$', 'app.views.profile'),
	url(r'^profile/img/(?P<action>edit|delete)$', 'app.views.change_profile_img'),
	url(r'^class/(?P<idclass>\d+)$', 'app.views.process_class'),
	url(r'^class/(?P<idlesson>\d+)/edit$', 'app.views.edit_class'),
	url(r'^forum$', 'app.views.forum'),
	url(r'^subjects$', 'app.views.subjects'),
	url(r'^seminars$', 'app.views.seminars'),
	url(r'^subjects/(?P<idsubj>\d+)$', 'app.views.subject'),
	url(r'^subjects/(?P<idsubj>\d+)/attendance$', 'app.views.subject_attendance'),
	url(r'^subjects/(?P<idsubj>\d+)/edit$', 'app.views.subject_edit'),
	url(r'^subjects/(?P<idsubj>\d+)/new_class$', 'app.views.create_class'),
	url(r'^img/(?P<path>.*)$', 'django.views.static.serve',
						{'document_root': 'static/images'}),
	url(r'^media/(?P<path>.*)$', 'django.views.static.serve', 
						{'document_root': settings.MEDIA_ROOT}),
	url(r'^css/(?P<path>.*)$', 'django.views.static.serve',
						{'document_root': 'static/css'}),
	url(r'^jscript/(?P<path>.*)$', 'django.views.static.serve',
						{'document_root': 'static/javascript'}),
	url(r'^lib/(?P<path>.*)$', 'django.views.static.serve',
						{'document_root': 'lib'}),
    # url(r'^URJCheckIn/', include('URJCheckIn.foo.urls')),
	url(r'control/attendance$', 'app.views.control_attendance'),
	url(r'^logout$', 'app.views.my_logout'),
	url(r'^login$', 'django.contrib.auth.views.login'),
	url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	url(r'^admin/', include(admin.site.urls)),
	url(r'^password_change/ajax$', 'app.views.password_change'),
	url(r'^password_change/$', 'django.contrib.auth.views.password_change'),
	url(r'^password_change/done/$', 'django.contrib.auth.views.password_change_done'),
	url(r'^password_reset/$', 'django.contrib.auth.views.password_reset'),
	url(r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done'),
	url(r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
		'django.contrib.auth.views.password_reset_confirm'),#TODO error, email no configurado
	url(r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete'),
	url(r'^.*$', 'app.views.not_found'),
)
