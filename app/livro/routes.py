from db_functions import *
from mysql.connector import Error
import uuid
from flask import Blueprint, render_template, request, redirect, session, jsonify, flash
from datetime import datetime, timedelta

livro = Blueprint('livro', __name__)

@livro.route('/livros')
def livros():
    nome_usuario = session.get('nome', "")
    logado = session.get('logado', False)
    nivel_usuario = session.get('nivelUsuario', None)

    if nivel_usuario == 'admin' or nivel_usuario == 'usuario':
        logado = session.get('logado', True)

    conexao, cursor = conectar_db()
    cursor.execute("SELECT * FROM livros")
    livros = cursor.fetchall()
    encerrar_db(cursor, conexao)

    return render_template('livros.html', logado=logado, titulo="Verbum - Livros", livros=livros, nome_usuario=nome_usuario)

@livro.route('/livro/<int:idLivro>')
def verlivro(idLivro):
    logado = session.get('logado', False)
    nivel_usuario = session.get('nivelUsuario', None)
    nome_usuario = session.get('nome', "")

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
            msg= f'Posição da lista de espera: {posicao}'
            return render_template('verlivro.html',  msg=msg, livro=livro, reserva_ativa=reserva_ativa, nome_usuario=nome_usuario, logado=logado)
        
    elif nivel_usuario == 'admin':
        logado = session.get('logado', True)

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

        cursor.execute("DELETE FROM listaespera WHERE idLivro = %s", (id,))
        conexao.commit()

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

    try:
        conexao, cursor = conectar_db()

        cursor.execute("""
        SELECT idUsuario FROM listaespera WHERE idLivro = %s and idUsuario = %s and status = 1
                       """, (idLivro, idUsuario))
        reserva_ativa = cursor.fetchone()

        if reserva_ativa:
            msg = 'Você já está na lista de espera deste livro'
            flash(msg, "success")
            posicao = verPosicao(idLivro, idUsuario)
            return redirect(f'/livro/{idLivro}')
        
        else:
            cursor.execute("""
                INSERT INTO listaespera (idLivro, idUsuario, dataReserva)
                VALUES (%s, %s, NOW())
            """, (idLivro, idUsuario))
            conexao.commit()
            posicao = verPosicao(idLivro, idUsuario)
            reserva_ativa = True
            msg = f'Parabéns! Você tem uma reserva! Sua posição é: {posicao}'
            flash(msg)

        return redirect(f'/livro/{idLivro}')
    
    except Exception as e:
        print(f"Erro ao realizar reserva: {e}")
        conexao.rollback()
        flash("Erro ao realizar a reserva, tente novamente mais tarde.")
        return redirect(f'/livro/{idLivro}')
    finally:
        conexao.close()

@livro.route('/listaespera/<int:idLivro>')
def lista_espera(idLivro):
    logado = session.get('logado', True)
    nome_usuario = session.get('nome', "")
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
        WHERE r.idLivro = %s AND r.status = 1
        ORDER BY r.dataReserva
    """, (idLivro,))
    lista_espera = cursor.fetchall()
    lista_espera = lista_espera or []

    conexao.close()

    return render_template('listaespera.html', livro=livro, lista_espera=lista_espera, logado=logado, nome_usuario=nome_usuario)

@livro.route('/livrosreservados')
def livrosreservados():
    logado = session.get('logado', True)
    nome_usuario = session.get('nome', "")
    idUsuario = session.get('idUsuario')

    if not idUsuario:
        return redirect('/login')

    conexao, cursor = conectar_db()

    try:
        cursor.execute("""
            SELECT l.idLivro, l.titulo, l.imagemCapa, le.dataReserva, e.dataDevolucao
            FROM listaespera le
            JOIN livros l ON le.idLivro = l.idLivro
            LEFT JOIN Emprestimos e ON e.idLivro = l.idLivro AND e.idUsuario = le.idUsuario
            WHERE le.idUsuario = %s
            ORDER BY le.dataReserva
        """, (idUsuario,))
        livros = cursor.fetchall()

        return render_template(
            "livrosreservados.html", 
            nome_usuario=nome_usuario, 
            logado=logado, 
            livros=livros
        )
    except Exception as e:
        print(f"Erro ao buscar livros reservados: {e}")
        return "Erro ao buscar livros reservados."
    finally:
        conexao.close()

@livro.route('/cancelareserva/<int:idLivro>', methods=['POST', 'GET'])
def cancelareserva(idLivro):
    idUsuario = session.get('idUsuario')

    try:
        conexao, cursor = conectar_db()

        cursor.execute("""
            DELETE FROM listaespera 
            WHERE idLivro = %s AND idUsuario = %s AND status = 1
        """, (idLivro, idUsuario))
        conexao.commit()

        return redirect(f'/livro/{idLivro}')
    
    except Exception as e:
        print(f"Erro ao cancelar reserva: {e}")
        return "Erro ao cancelar a reserva, tente novamente mais tarde."
    finally:
        conexao.close()

@livro.route('/busca', methods=['POST'])
def busca():
    logado = session.get('logado', True)
    nome_usuario = session.get('nome', "")
    nivel_usuario = session.get('nivel_usuario', None)
    busca = request.form['busca']

    if nivel_usuario == 'usuario' or nivel_usuario == 'admin':
        logado = session.get('logado', True)

    try:
        conexao, cursor = conectar_db()

        cursor.execute("SELECT * FROM livros WHERE titulo LIKE %s", (f"{busca}%",))
        livros_encontrados = cursor.fetchall()

        return render_template('livros.html', 
                               logado=logado, 
                               nome_usuario=nome_usuario, 
                               livros=livros_encontrados
                               )
    except Exception as e:
        print(f"Erro ao realizar a busca: {e}")
        return "Erro ao realizar a busca. Tente novamente mais tarde."
    finally:
        encerrar_db(cursor, conexao)

from flask import Flask, render_template, redirect, flash, url_for
from datetime import datetime, timedelta

@livro.route('/emprestimo/<int:idListaEspera>')
def fazer_emprestimo(idListaEspera):
    try:
        conexao, cursor = conectar_db()

        query = "UPDATE listaespera SET status = 0 WHERE idListaEspera = %s"
        cursor.execute(query, (idListaEspera,))
        conexao.commit()
        
        query = "SELECT idLivro, idUsuario FROM listaespera WHERE idListaEspera = %s"
        cursor.execute(query, (idListaEspera,))
        dados = cursor.fetchone()

        data_emprestimo = datetime.now()
        data_devolucao = data_emprestimo + timedelta(days=30)
        data_emprestimo_f = data_emprestimo.strftime('%Y-%m-%d')
        data_devolucao_f = data_devolucao.strftime('%Y-%m-%d')

        query_inserir = """
            INSERT INTO Emprestimos (idLivro, idUsuario, dataEmprestimo, dataDevolucao)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query_inserir, (dados['idLivro'], dados['idUsuario'], data_emprestimo_f, data_devolucao_f))
        conexao.commit()

        flash("Empréstimo realizado com sucesso!", "success")

    except Exception as e:
        conexao.rollback()
        flash(f"Erro ao processar o empréstimo: {str(e)}", "error")

    finally:
        encerrar_db(conexao, cursor)

    return redirect(url_for('main.adm'))
