from django.conf.urls.defaults import patterns, include, url

key_patterns = patterns('API.views',
        url(r'^delete/$', 'delete_key'),
        url(r'^purge/$', 'delete_key', {'purge': True}),
        url(r'^edit/$', 'edit_keys'),
        )

urlpatterns = patterns('API.views',
        url(r'^key/$', 'api_key_dialog'),
        url(r'^key/new/$', 'edit_keys'),
        url(r'^key/(?P<key_id>\d+)/', include(key_patterns)),
        )
