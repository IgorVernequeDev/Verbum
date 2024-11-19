from db_functions import *
from mysql.connector import Error
import uuid
from flask import Blueprint, render_template, request, redirect, session, jsonify

livro = Blueprint('livro', __name__)

@livro.route('/livros')
def livros():
    nome_usuario = session.get('nome', "")
    logado = session.get('logado')
    conexao, cursor = conectar_db()
    cursor.execute("SELECT * FROM livros")
    livros = cursor.fetchall()
    encerrar_db(cursor, conexao)
    return render_template('livros.html', logado=logado, titulo="Verbum - Livros", livros=livros, nome_usuario=nome_usuario)

@livro.route('/livro/<int:idLivro>')
def verlivro(idLivro):
    nivel_usuario = session.get('nivelUsuario', 'usuario')
    nome_usuario = session.get('nome', "")
    logado = session.get('logado', True)

    livro = buscarLivro(idLivro)
    conexao, cursor = conectar_db()

    if nivel_usuario == 'usuario':
        idUsuario = session['idUsuario']
        cursor.execute("""
        SELECT idUsuario FROM listaespera WHERE idLivro = %s and idUsuario = %s and status = 1
                        """, (idLivro, idUsuario))
    
        reserva_ativa = cursor.fetchone()
        encerrar_db(conexao, cursor)

        if reserva_ativa:
            posicao = verPosicao(idLivro, idUsuario)
            msg= f'Você já está na lista de espera deste livro. Você está na posição {posicao}'
            return render_template('verlivro.html',  msg=msg, livro=livro, reserva_ativa=reserva_ativa, nome_usuario=nome_usuario)

    return render_template('verlivro.html', logado=logado, titulo="Verbum - Livros", livro=livro, nome_usuario=nome_usuario, verlivro=True)

@livro.route('/cadastrarlivro')
def cadastrarlivro():
    logado = session.get('logado', True)

    try:
        conexao, cursor = conectar_db()
        cursor.execute("SELECT * from editoras")
        editoras = cursor.fetchall()
        cursor.execute("SELECT * from autores")
        autores = cursor.fetchall()

        return render_template('cadlivro.html', editoras=editoras, autores=autores, logado=logado, titulo="Verbum ADM - Cadastro de livros")
    except Exception as erro:
        return f"Erro {erro}"
    except Error as erro:
        return f"Erro BD {erro}"

    finally:
        encerrar_db(cursor, conexao)

@livro.route('/cadlivro', methods=['GET', 'POST'])
def cadlivro():
    conexao, cursor = conectar_db()

    if request.method == 'POST':
        titulo = request.form['titulo'].title()
        descricao = request.form['descricao'].title()
        numero_paginas = request.form['numero_paginas']
        genero = request.form['genero'].title()
        imagemCapa = request.files['imagemCapa']
        anoPublicacao = request.form['anoPublicacao']
        quantidade = request.form['quantidade']
        idAutor = request.form['autor']
        idEditora = request.form['editora']

    id_foto = str(uuid.uuid4().hex)
    filename = id_foto + titulo + '.png'
    imagemCapa.save("static/img/livros/" + filename)

    cursor.execute(
        'INSERT INTO livros (idAutor, idEditora, titulo, descricao, numero_paginas, genero, imagemCapa, anoPublicacao, quantidade) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
        (idAutor, idEditora, titulo, descricao, numero_paginas,
         genero, filename, anoPublicacao, quantidade)
    )

    conexao.commit()
    conexao.close()
    return redirect('/adm')

@livro.route('/cadautor', methods=['GET', 'POST'])
def cadautor():
    if request.method == 'POST':
        dados = request.get_json()
        autor = dados.get('nome')
        try:
            conexao, cursor = conectar_db()
            cursor.execute(
                "INSERT INTO autores (nomeAutor) VALUES (%s)", (autor,))
            conexao.commit()
            return jsonify({'success': True, 'id': cursor.lastrowid}), 200
        except Exception as erro:
            return f"Erro {erro}"
        except Error as erro:
            return f"Erro BD {erro}"
        finally:
            encerrar_db(cursor, conexao)

@livro.route('/cadeditora', methods=['GET', 'POST'])
def cadeditora():
    if request.method == 'POST':
        dados = request.get_json()
        editora = dados.get('nome_editora')
        try:
            conexao, cursor = conectar_db()
            cursor.execute(
                "INSERT INTO editoras (nomeEditora) VALUES (%s)", (editora,))
            conexao.commit()
            return jsonify({'success': True, 'id': cursor.lastrowid}), 200
        except Exception as erro:
            return f"Erro {erro}"
        except Error as erro:
            return f"Erro BD {erro}"
        finally:
            encerrar_db(cursor, conexao)

@livro.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    logado = session.get('logado', True)
    if request.method == 'GET':
        try:
            conexao, cursor = conectar_db()

            cursor.execute("""
                SELECT livros.*, autores.nomeAutor, editoras.nomeEditora
                FROM livros
                JOIN autores ON livros.idAutor = autores.idAutor
                JOIN editoras ON livros.idEditora = editoras.idEditora
                WHERE livros.idLivro = %s
            """, (id,))

            livro = cursor.fetchone()

            cursor.execute("SELECT * FROM autores")
            autores = cursor.fetchall()

            cursor.execute("SELECT * FROM editoras")
            editoras = cursor.fetchall()

            return render_template('editarlivro.html', livro=livro, autores=autores, editoras=editoras, logado=logado)
        except Exception as erro:
            return f"Erro {erro}"
        finally:
            encerrar_db(cursor, conexao)

    elif request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        numero_paginas = request.form['numero_paginas']
        genero = request.form['genero']
        idEditora = request.form['editora']
        anoPublicacao = request.form['anoPublicacao']
        quantidade = request.form['quantidade']
        idAutor = request.form['autor']

        imagemCapa = request.files.get('imagemCapa')
        try:
            conexao, cursor = conectar_db()

            if imagemCapa:
                id_foto = str(uuid.uuid4().hex)
                filename = id_foto + titulo + '.png'
                imagemCapa.save("static/img/livros/" + filename)

                cursor.execute("""
                    UPDATE livros
                    SET idAutor = %s, idEditora = %s, titulo = %s, descricao = %s, numero_paginas = %s, genero = %s, anoPublicacao = %s, quantidade = %s, imagemCapa = %s
                    WHERE idLivro = %s
                """, (idAutor, idEditora, titulo, descricao, numero_paginas, genero, anoPublicacao, quantidade, filename, id))
            else:
                cursor.execute("""
                    UPDATE livros
                    SET idAutor = %s, idEditora = %s, titulo = %s, descricao = %s, numero_paginas = %s, genero = %s, anoPublicacao = %s, quantidade = %s
                    WHERE idLivro = %s
                """, (idAutor, idEditora, titulo, descricao, numero_paginas, genero, anoPublicacao, quantidade, id))

            conexao.commit()

            return redirect('/livros')
        except Exception as erro:
            return f"Erro {erro}"
        finally:
            encerrar_db(cursor, conexao)

@livro.route('/excluir/<int:id>', methods=['GET', 'POST'])
def excluir(id):
    try:
        conexao, cursor = conectar_db()

        cursor.execute("DELETE FROM livros WHERE idLivro = %s", (id,))
        conexao.commit()

        return redirect('/livros')
    except Exception as erro:
        return f"Erro ao tentar excluir o livro: {erro}"
    finally:
        encerrar_db(cursor, conexao)

@livro.route('/reservar/<int:idLivro>', methods=['GET'])
def reservar(idLivro):
    idUsuario = session['idUsuario']

    if not session:
        return redirect('/login')
    
    livro = buscarLivro(idLivro)

    try:
        conexao, cursor = conectar_db()

        cursor.execute("""
        SELECT idUsuario FROM listaespera WHERE idLivro = %s and idUsuario = %s and status = 1
                       """, (idLivro, idUsuario))
        reserva_ativa = cursor.fetchone()

        if reserva_ativa:
            msg='Você já está na lista de espera deste livro'
            posicao = verPosicao(idLivro, idUsuario)
            return render_template('verlivro.html',  msg=msg, livro=livro, posicao=posicao)
        
        else:
            cursor.execute("""
                INSERT INTO listaespera (idLivro, idUsuario, dataReserva)
                VALUES (%s, %s, NOW())
            """, (idLivro, idUsuario))
            conexao.commit()
            posicao = verPosicao(idLivro, idUsuario)
            reserva_ativa = True
            msg=f'Parabéns! Você tem uma reserva! Sua posição é: {posicao}'


        return render_template('verlivro.html',  msg=msg, posicao=posicao, livro=livro, reserva_ativa=reserva_ativa)
    
    except Exception as e:
        print(f"Erro ao realizar reserva: {e}")
        conexao.rollback()
        return "Erro ao realizar a reserva, tente novamente mais tarde."
    finally:
        conexao.close()

@livro.route('/listaespera/<int:idLivro>')
def lista_espera(idLivro):
    logado = session.get('logado', True)
    conexao, cursor = conectar_db()

    cursor.execute("SELECT * FROM Livros WHERE idLivro = %s", (idLivro,))
    livro = cursor.fetchone()

    if not livro:
        conexao.close()
        return "Livro não encontrado", 404

    cursor.execute("""
        SELECT u.nome, u.serie, r.dataReserva
        FROM listaespera r
        JOIN Usuarios u ON r.idUsuario = u.idUsuario
        WHERE r.idLivro = %s
        ORDER BY r.dataReserva
    """, (idLivro,))
    lista_espera = cursor.fetchall()

    conexao.close()

    return render_template('listaespera.html', livro=livro, lista_espera=lista_espera, logado=logado)