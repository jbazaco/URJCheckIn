from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

#For dajaxice
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
dajaxice_autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'app.views.home'),
	url(r'^checkin$', 'app.views.checkin'),
	url(r'^profile/view/(\d+)$', 'app.views.profile'),
	url(r'^profile/img/(\d+)$', 'app.views.profile_img'),
	url(r'^class/(\d+)$', 'app.views.process_class'),
	url(r'^forum$', 'app.views.forum'),
	url(r'^subjects$', 'app.views.subjects'),
	url(r'^subjects/(\d+)$', 'app.views.subject'),
	url(r'^img/(?P<path>.*)$', 'django.views.static.serve',
						{'document_root': 'static/images'}),
	url(r'^css/(?P<path>.*)$', 'django.views.static.serve',
						{'document_root': 'static/css'}),
	url(r'^jscript/(?P<path>.*)$', 'django.views.static.serve',
						{'document_root': 'static/javascript'}),
	url(r'^lib/(?P<path>.*)$', 'django.views.static.serve',
						{'document_root': 'lib'}),
    # url(r'^URJCheckIn/', include('URJCheckIn.foo.urls')),

	url(r'^logout$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
	url(r'^login$', 'django.contrib.auth.views.login'),
	url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	url(r'^admin/', include(admin.site.urls)),

	url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
	url(r'^.*$', 'app.views.not_found'),
)

#For dajaxice
urlpatterns += staticfiles_urlpatterns()
