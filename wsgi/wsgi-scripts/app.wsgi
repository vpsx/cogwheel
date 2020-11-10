## Put the application files on the python load path:
import sys
sys.path.insert(0, '/var/www/wsgi/src')

from main import app as application
