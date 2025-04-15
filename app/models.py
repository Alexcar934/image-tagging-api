import mysql.connector  
import os  

db = None  # variable global donde guardaremos la conexión

def init_db():
    global db
    db = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "db"),  
        user=os.getenv("MYSQL_USER", "pc3"),
        password=os.getenv("MYSQL_PASSWORD", "pc3-mbit"),
        database=os.getenv("MYSQL_DATABASE", "pc3_Database")
    )

def get_db():
    if db is None:
        raise Exception("Base de datos no inicializada. Llama a init_db() primero.")
    return db