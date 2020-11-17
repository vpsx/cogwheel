from flask import Flask, request
app = Flask(__name__)

# Docs on how Shibboleth info is passed from server to application:
# https://wiki.shibboleth.net/confluence/display/SP3/ApplicationIntegration
# https://wiki.shibboleth.net/confluence/display/SP3/AttributeAccess#AttributeAccess-REMOTE_USER

@app.route('/')
def hello_world():
    return 'Hello, World! I\'m a Flask app!'


@app.route('/apache')
def apache():
    # Inspect request context
    print("request:")
    print(request)
    print(dir(request))
    print(request.remote_user)
    return "REMOTE_USER is..... " + request.remote_user
