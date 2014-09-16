import os, sys

sys.path[0:0] = ["/home/rm22/django/usr/local/lib/python2.6/site-packages"]
#Calculate the path based on the location of the WSGI script.
apache_configuration= os.path.dirname(__file__)
project = os.path.dirname(apache_configuration)
workspace = os.path.abspath(os.path.dirname(project))
sys.path.append(workspace)
sys.path.append(project)
#print >>sys.stderr, workspace 
#print >>sys.stderr, apache_configuration 
#Add the path to 3rd party django application and to django itself.
#sys.path.append('C:\\yml\\_myScript_\\dj_things\\web_development\\svn_views\\django_src\\trunk')
#sys.path.append('C:\\yml\\_myScript_\\dj_things\\web_development\\svn_views\\django-registration')

os.environ['DJANGO_SETTINGS_MODULE'] = 'competitions.settings'
os.environ['LC_ALL'] = 'ru_RU.utf8'
os.environ['LANG'] = 'ru_RU.utf8'
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
