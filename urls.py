from django.conf.urls.defaults import *
from django.conf import settings
from django.views import static

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^EventMailer/', include('EventMailer.foo.urls')),
    (r'^$','authentication_eventmailer.views.index'),
    (r'^authenticate/','authentication_eventmailer.views.authentication'),
    (r'^event_creation/','authentication_eventmailer.views.event_creation'),
    (r'^save_event/','authentication_eventmailer.views.save_event'),
    (r'^send_emails/','authentication_eventmailer.views.send_emails'),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/', include(admin.site.urls)),
)


urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$',
        'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
            'show_indexes': True,
        },
    ),
)
