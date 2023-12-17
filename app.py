from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from flask import Flask,render_template, request
from prometheus_client import Gauge, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
import os 


app = Flask(__name__)

xray_daemon_address = os.environ.get('XRAY_ADDRESS') 


xray_recorder.configure(service='flask-app', daemon_address=xray_daemon_address)
XRayMiddleware(app, xray_recorder) 
plugins = ('EC2Plugin',)
xray_recorder.configure(plugins=plugins)



 

@app.route('/')  
def message():  
      return "<html><body><h1>Hi, welcome to the website</h1><h2><a href='/form'> Login</a> </h2></body></html>"  
@app.route('/form')
def form():
    return render_template('form.html')
 
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return "<h1> Login via the login <a href='/form'> Form </a> </h1>"
     
cluster_load = Gauge('cluster_load', 'Current cluster load')

@app.route('/cluster_load', methods=['PUT', 'GET'])
def cluster_load_handler():
    if request.method == 'PUT':
        load = request.args.get('value', default=0, type=float)
        cluster_load.set(load)
        return 'Cluster load set to {}'.format(load), 200
    else:
        return 'Current cluster load: {}'.format(cluster_load._value.get()), 200
    
# Create a Prometheus WSGI middleware
metrics_app = make_wsgi_app()

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': metrics_app
})

if __name__ == '__main__':  
   app.run(debug = True, host='0.0.0.0', port="5000")

