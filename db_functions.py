import mysql.connector
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

def buscarLivro(idLivro):
    conexao, cursor = conectar_db()
    cursor.execute("""
            SELECT livros.*, autores.nomeAutor, editoras.nomeEditora
            FROM livros
            JOIN autores ON livros.idAutor = autores.idAutor
            JOIN editoras ON livros.idEditora = editoras.idEditora
            WHERE livros.idLivro = %s
        """, (idLivro,))
    livro = cursor.fetchone()
    encerrar_db(conexao, cursor)
    return livro

def verPosicao(idLivro, idUsuario):
    conexao, cursor = conectar_db()
    cursor.execute("""
SELECT idUsuario FROM listaespera WHERE idLivro = %s and status = 1 ORDER BY datareserva ASC
                       """, (idLivro,))
    lista = cursor.fetchall()
    posicao = None           
    for index, reserva in enumerate(lista):
        if reserva['idUsuario'] == idUsuario:
            posicao = index + 1
            break
    print(posicao)

    encerrar_db(conexao, cursor)

    return posicao