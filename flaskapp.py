from flask import Flask
from flask import Response
flaskApp = Flask('flaskapp')

@flaskApp.route('/hello')
def helloWorld():
    return Response(
        'Hello world from Flask!\n',
        mimetype='text/plain'
    )

app = flaskApp.wsgi_app
