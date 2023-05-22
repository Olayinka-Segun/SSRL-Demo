import mysql.connector





db = mysql.connector.connect (
  host="localhost",
  user="root",
  password="sege_d_boy@2002",
  database = 'smartdb'
  
)
mycursor=db.cursor()


#cursor = db.connection.cursor(MySQLdb.cursors.DictCursor) 

