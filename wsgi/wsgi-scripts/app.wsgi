## Put the application files on the python load path:
import sys
sys.path.insert(0, '/var/www/wsgi/src')

from main import app as application



# FOR ENABLING INTERACTIVE DEBUGGER (Uncomment to enable):
# Wrap the application in this Debugger class.
#class Debugger:
#
#    def __init__(self, object):
#        self.__object = object
#
#    def __call__(self, *args, **kwargs):
#        import pdb, sys
#        debugger = pdb.Pdb()
#        debugger.use_rawinput = 0
#        debugger.reset()
#        sys.settrace(debugger.trace_dispatch)
#
#        try:
#            return self.__object(*args, **kwargs)
#        finally:
#            debugger.quitting = 1
#            sys.settrace(None)
#
#application = Debugger(application)
