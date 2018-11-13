import wsgiref
from flask import render_template, request
from flaskext.mysql import MySQL
import mysql.connector




mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'project1'
app.config['MYSQL_DATABASE_HOST'] = '3306'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
mysql=MySQL(app)
conn = mysql.connect()
cursor =conn.cursor()

cursor.execute("select sname,roll_no,rank from cet_rank where roll_no='ko111;")
data=cursor.fetchall()
print(data)