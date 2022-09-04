import mysql.connector
from sqlalchemy import create_engine

connection = mysql.connector.connect(host='192.168.0.45',
                                     database='iut_database',
                                     user='root',
                                     password='gabrielmassoN01612!')

engine = create_engine("mysql+mysqldb://root:gabrielmassoN01612!@192.168.0.45/iut_database")

cursor = connection.cursor()
