import mysql.connector
from sqlalchemy import create_engine

connection = mysql.connector.connect(host='localhost',
                                     database='iut_database',
                                     user='root',
                                     password='gabrielmassoN01612')

engine = create_engine("mysql+mysqldb://root:gabrielmassoN01612@localhost/iut_database")

cursor = connection.cursor()
