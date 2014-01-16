from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'app.views.home'),
	url(r'^checkin$', 'app.views.checkin'),
	url(r'^profile/view/(\w+)$', 'app.views.profile'),
	url(r'^profile/img/(\w+)$', 'app.views.profile_img'),
	url(r'^class/(\w+)$', 'app.views.process_class'),
	url(r'^img/(?P<path>.*)$', 'django.views.static.serve',
						{'document_root': 'static/images'}),
	url(r'^css/(?P<path>.*)$', 'django.views.static.serve',
						{'document_root': 'static/css'}),
	url(r'^jscript/(?P<path>.*)$', 'django.views.static.serve',
						{'document_root': 'static/javascript'}),
	url(r'^lib/(?P<path>.*)$', 'django.views.static.serve',
						{'document_root': 'lib'}),
    # url(r'^URJCheckIn/', include('URJCheckIn.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
	url(r'^.*$', 'app.views.not_found'),
)
