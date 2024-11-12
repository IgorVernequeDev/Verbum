from db_functions import conectar_db, encerrar_db
from routes import *
from mysql.connector import Error
import uuid
from flask import render_template, request, redirect, session, jsonify
from datetime import date

@app.route('/livros')
def livros():
    nome_usuario = session.get('nome', "")
    logado = session.get('logado', True)
    conexao, cursor = conectar_db()
    cursor.execute("SELECT * FROM livros")
    livros = cursor.fetchall()
    encerrar_db(cursor, conexao)
    return render_template('livros.html', logado=logado, titulo="Verbum - Livros", livros=livros, nome_usuario=nome_usuario)

@app.route('/livro/<int:id>')
def livro(id):
    nome_usuario = session.get('nome', "")
    logado = session.get('logado', True)
    conexao, cursor = conectar_db()

    try:
        cursor.execute("""
            SELECT livros.*, autores.nomeAutor, editoras.nomeEditora
            FROM livros
            JOIN autores ON livros.idAutor = autores.idAutor
            JOIN editoras ON livros.idEditora = editoras.idEditora
            WHERE livros.idLivro = %s
        """, (id,))
        livro = cursor.fetchone()

        if livro is None:
            return render_template('erro.html', mensagem="Livro não encontrado"), 404

        return render_template('verlivro.html', logado=logado, titulo="Verbum - Livros", livro=livro, nome_usuario=nome_usuario, verlivro=True)

    finally:
        encerrar_db(cursor, conexao)

@app.route('/home')
def home():
    nome_usuario = session.get('nome', "")
    logado = session.get('logado', True)

    conexao, cursor = conectar_db()

    encerrar_db(cursor, conexao)

    return render_template('index.html', logado=logado, nome_usuario=nome_usuario, titulo="Verbum - Home")

@app.route('/cadastrarlivro')
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

@app.route('/login', methods=['POST'])
def logar():
    email = request.form['email']
    senha = request.form['senha']

    conexao, cursor = conectar_db()

    query = "SELECT idUsuario, nome, email, senha FROM usuarios WHERE email = %s"
    cursor.execute(query, (email,))
    usuario = cursor.fetchone()

    cursor.close()
    conexao.close()

    if email == 'admin@gmail.com' and senha == '123':
        session['nivelUsuario'] = 'admin'
        return redirect('/adm')

    if usuario:
        idUsuario = usuario['idUsuario']
        nome = usuario['nome']
        senha_db = usuario['senha']

        if senha == senha_db:
            session['logado'] = True
            session['idUsuario'] = idUsuario
            session['nome'] = nome
            session['nivelUsuario'] = 'usuario'
            return redirect('/home')
        else:
            return render_template("login.html", msg="Senha incorreta!")

    else:
        return render_template("login.html", msg="Usuário não encontrado!")

@app.route('/cadlivro', methods=['GET', 'POST'])
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

@app.route('/cadautor', methods=['GET', 'POST'])
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

@app.route('/cadeditora', methods=['GET', 'POST'])
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

@app.route('/cadaluno', methods=['POST'])
def cadaluno():
    conexao, cursor = conectar_db()

    nome = request.form['nome']
    nome = nome.title()
    email = request.form['email']
    serie = request.form['serie']
    letra = request.form['letra']
    senha = request.form['senha']
    confirmasenha = request.form['confirmasenha']

    serie = serie + ' ' + letra

    if senha == confirmasenha:
        cursor.execute(
            'INSERT INTO usuarios (nome, email, serie, senha) VALUES (%s, %s, %s, %s)', (nome, email, serie, senha))
        conexao.commit()
        conexao.close()

    else:
        return render_template("cadaluno.html", msg="As senhas não se coincidem!")

    return redirect('/adm')

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
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

            return render_template('editarlivro.html', livro=livro, autores=autores, editoras=editoras)
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

@app.route('/excluir/<int:id>', methods=['GET', 'POST'])
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

@app.route('/reservar/<int:idLivro>', methods=['POST'])
def reservar(idLivro):
    idUsuario = session.get('idUsuario')

    if not idUsuario:
        return "Usuário não autenticado", 403

    conexao, cursor = conectar_db()

    try:
        cursor.execute("""
            INSERT INTO listaespera (idLivro, idUsuario, dataReserva)
            VALUES (%s, %s, NOW())
        """, (idLivro, idUsuario))

        conexao.commit()

        return redirect(f'/listaespera/{idLivro}')
    except Exception as e:
        print(f"Erro ao realizar reserva: {e}")
        conexao.rollback()
        return "Erro ao realizar a reserva, tente novamente mais tarde."
    finally:
        conexao.close()

@app.route('/listaespera/<int:idLivro>')
def lista_espera(idLivro):
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

    return render_template('listaespera.html', livro=livro, lista_espera=lista_espera)

def adicionar_a_lista_espera(id_livro, id_usuario):
    conexao = conectar_db()
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT MAX(posicaoEspera) FROM ListaEspera WHERE idLivro = %s", (id_livro,))
    posicao_atual = cursor.fetchone()[0]

    nova_posicao = 0 if posicao_atual is None else posicao_atual + 1

    cursor.execute("""
        INSERT INTO ListaEspera (idLivro, idUsuario, posicaoEspera, dataReserva)
        VALUES (%s, %s, %s, %s)
    """, (id_livro, id_usuario, nova_posicao, date.today()))

    conexao.commit()
    cursor.close()
    conexao.close()
    return jsonify({"success": True, "mensagem": "Reserva adicionada à lista de espera."})

@app.route('/api/lista_espera/<int:id_livro>')
def get_lista_espera(id_livro):
    conexao = conectar_db()
    cursor = conexao.cursor(dictionary=True)
    cursor.execute("""
        SELECT Usuarios.nome AS usuarioNome, ListaEspera.posicaoEspera
        FROM ListaEspera
        JOIN Usuarios ON ListaEspera.idUsuario = Usuarios.idUsuario
        WHERE ListaEspera.idLivro = %s
        ORDER BY ListaEspera.posicaoEspera
    """, (id_livro,))
    lista_espera = cursor.fetchall()
    cursor.close()
    conexao.close()
    return jsonify(lista_espera)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)