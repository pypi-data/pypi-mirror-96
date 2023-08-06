WSGI Preload
============

Preload your WSGI applications with specified URLs during startup.


Add this to the end of your .wsgi file:

~~~~
:::python
import wsgipreload
wsgipreload.preload(application, urls=['/', '/foo', '/bar'])
~~~~

If you are using mod_wsgi, specify the `process-group` and `application-group` on your `WSGIScriptAlias` directive so that it will preload properly.  The `process-group` must match what you specify with `WSGIProcessGroup` in your config file.  Details at <https://modwsgi.readthedocs.io/en/develop/release-notes/version-3.0.html#features-added> (section 2)

~~~~
WSGIScriptAlias / /etc/httpd/conf.d/myapp.wsgi process-group=myapp application-group=%{GLOBAL}
~~~~

Bonus!  A helper function is included to pick a few URLs from the beginning of a log file.  Use this if you don't want to hard-code all the URLs into your wsgi file.

~~~~
:::python
import wsgipreload
urls = {'/'}
try:
    with open('/var/local/log/httpd-access_log') as log_file:
        urls |= wsgipreload.urls_from_log(log_file, num=5)
except Exception as e:
    print("preload error on logs")
    import traceback
    traceback.print_exc()

wsgipreload.preload(application, urls=urls)
~~~~