
import os
from flask import Flask
from flask_jwt_extended import JWTManager
app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'super-secret' #change later
app.config['PROPAGATE_EXCEPTIONS'] = True

jwt = JWTManager(app)