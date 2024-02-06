import MySQLdb.cursors
import mysql.connector
from sqlalchemy import create_engine
import pymysql

connection = mysql.connector.connect(host='192.168.0.29',
                                     database='IUT_DB',
                                     user='root',
                                     password='none')
connection.autocommit = True
engine = create_engine("mysql+mysqldb://root:gabrielmassoN01612!@192.168.0.29/IUT_DB")

cursor = connection.cursor(buffered=True)
