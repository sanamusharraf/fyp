# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 19:36:03 2019

@author: bushr
"""

from app import app
from flaskext.mysql import MySQL

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'aayeshalibra7*7=49'
app.config['MYSQL_DATABASE_DB'] = 'fyp'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)