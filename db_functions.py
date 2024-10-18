import mysql.connector
from mysql.connector import connect, Error
from config import *

def conectar_db():
    conexao = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conexao.cursor(dictionary=True)
    return conexao, cursor

def encerrar_db(cursor, conexao):
    cursor.close()
    conexao.close()