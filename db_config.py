# -*- coding: utf-8 -*-
"""
Created on Sun Mar 24 19:36:03 2019

@author: bushr
"""

from app import app
from flaskext.mysql import MySQL

mysql = MySQL()
 
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'BOhdaEyC26'
app.config['MYSQL_DATABASE_PASSWORD'] = 'qTv3OMHTmk'
app.config['MYSQL_DATABASE_DB'] = 'BOhdaEyC26'
app.config['MYSQL_DATABASE_HOST'] = 'Remotemysql.com'
mysql.init_app(app)