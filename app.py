# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 19:34:13 2019

@author: bushr
"""

from flask import Flask
from flask_jwt_extended import JWTManager
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super-secret' #change later
app.config['PROPAGATE_EXCEPTIONS'] = True

app = Flask(__name__)