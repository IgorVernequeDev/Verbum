from db_functions import conectar_db, encerrar_db
from routes import *
from mysql.connector import Error
import uuid
from flask import render_template, request, redirect, session, jsonify
from datetime import date

@app.route('/livros')
def livros():
    logado = session.get('logado', True)
    conexao, cursor = conectar_db()
    cursor.execute("SELECT * FROM livros")
    livros = cursor.fetchall()
    encerrar_db(cursor, conexao)
    return render_template('livros.html', logado=logado, titulo="Verbum - Livros", livros=livros)

@app.route('/livro/<int:id>')
def livro(id):
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
        
        return render_template('verlivro.html', logado=logado, titulo="Verbum - Livros", livro=livro, verlivro=True)

    finally:
        encerrar_db(cursor, conexao)

@app.route('/home')
def home():
    logado = session.get('logado', True)
    nome_usuario = session.get('nome', "")

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
        email_db = usuario['email']
        senha_db = usuario['senha']

        if senha == senha_db:
            session['logado'] = True
            session['idUsuario'] = idUsuario
            session['nome'] = nome
            return redirect('/home')
        else:
            return render_template("login.html", msg="Senha incorreta!")

    else:
        return render_template("login.html", msg="Usuário não encontrado!")
    
@app.route('/listaespera/<int:id>') 
def listaespera(id):
    logado = session.get('logado', True)
    try:
        conexao, cursor = conectar_db()
        
        cursor.execute("SELECT titulo FROM livros WHERE idLivro = %s", (id,))
        livro = cursor.fetchone()

        if not livro:
            return "Livro não encontrado.", 404

        cursor.execute("""
            SELECT u.nome AS nome, u.serie AS serie, r.dataReserva AS dataReserva
            FROM reservas r
            JOIN usuarios u ON r.idUsuario = u.idUsuario
            WHERE r.idLivro = %s
            ORDER BY r.dataReserva
        """, (id,))
        lista_espera = cursor.fetchall()

        encerrar_db(cursor, conexao)

        return render_template(
            'listaespera.html',
            logado=logado,
            titulo="Verbum - Lista de Espera",
            livro=livro,
            lista_espera=lista_espera
        )
    except Exception as erro:
        return f"Erro ao acessar a lista de espera: {erro}"
    
def adicionar_a_lista_espera(id_livro, id_usuario):
    conexao = conectar_db()
    cursor = conexao.cursor()

    cursor.execute("SELECT MAX(posicaoEspera) FROM ListaEspera WHERE idLivro = %s", (id_livro,))
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

# def enviar_notificacao(id_usuario, mensagem):
#     conexao = 
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO Notificacoes (idUsuario, mensagem, data) VALUES (%s, %s, %s)", (id_usuario, mensagem, date.today()))
#     conn.commit()
#     cursor.close()
#     conn.close()

# def liberar_livro(id_livro):
#     conexao = conectar_db()
#     cursor = conexao.cursor()

#     cursor.execute("SELECT idUsuario FROM ListaEspera WHERE idLivro = %s AND posicaoEspera = 0", (id_livro,))
#     usuario_id = cursor.fetchone()

#     if usuario_id:
#         enviar_notificacao(usuario_id, f"O livro '{id_livro}' está disponível para empréstimo.")

#         cursor.execute("DELETE FROM ListaEspera WHERE idLivro = %s AND posicaoEspera = 0", (id_livro,))
#         conexao.commit()

#         cursor.execute("""
#             UPDATE ListaEspera
#             SET posicaoEspera = posicaoEspera - 1
#             WHERE idLivro = %s
#         """, (id_livro,))
#         conexao.commit()

#     cursor.close()
#     conexao.close()

@app.route('/cadlivro', methods=['POST'])
def cadlivro():
    conexao, cursor = conectar_db()

    titulo = request.form['titulo'].title()
    descricao = request.form['descricao'].title()
    numero_paginas = request.form['numero_paginas']
    genero = request.form['genero'].title()
    imagemCapa = request.files['imagemCapa']
    anoPublicacao = request.form['anoPublicacao']
    quantidade = request.form['quantidade']
    idAutor = request.form['autor']
    idEditora = request.form['editora']

    # Valida se idAutor e idEditora são números inteiros válidos
    if not idAutor.isdigit() or not idEditora.isdigit():
        # Redireciona ou retorna uma mensagem de erro caso os valores sejam inválidos
        return "Erro: Autor ou Editora inválidos.", 400

    id_foto = str(uuid.uuid4().hex)
    filename = id_foto + titulo + '.png'
    imagemCapa.save("static/img/livros/" + filename)

    cursor.execute(
        'INSERT INTO livros (idAutor, idEditora, titulo, descricao, numero_paginas, genero, imagemCapa, anoPublicacao, quantidade) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
        (idAutor, idEditora, titulo, descricao, numero_paginas, genero, filename, anoPublicacao, quantidade)
    )

    conexao.commit()
    conexao.close()
    return render_template('adm_index.html')


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

@app.route('/cadautor', methods=['GET', 'POST'])
def cadautor():

    if request.method == 'GET':
        try:
            conexao, cursor = conectar_db()
            cursor.execute("SELECT * from autores")
            autores = cursor.fetchall()
            return render_template("cadautor.html", autores=autores)
        except Exception as erro:
            return f"Erro {erro}"
        except Error as erro:
            return f"Erro BD {erro}"
        finally:
            encerrar_db(cursor, conexao)

    if request.method == 'POST':
        dados = request.get_json()
        autor = dados.get('nome')
        try:
            conexao, cursor = conectar_db()
            cursor.execute("INSERT INTO autores VALUES (null, %s)", (autor,))
            conexao.commit()

            return jsonify({'success': True}), 200
        except Exception as erro:
            return f"Erro {erro}"
        except Error as erro:
            return f"Erro BD {erro}"
        finally:
            encerrar_db(cursor, conexao)
    else:
        try:
            conexao, cursor = conectar_db()
            cursor.execute("SELECT * from autor")
            autores = cursor.fetchall()
            return render_template('/cadautor', autores=autores)


        except Exception as erro:
            return f"Erro {erro}"
        except Error as erro:
            return f"Erro BD {erro}"
        finally:
            encerrar_db(cursor, conexao)

@app.route('/cadeditora', methods=['GET', 'POST'])
def cadeditora():
    if request.method == 'GET':
        try:
            conexao, cursor = conectar_db()
            cursor.execute("SELECT * from editoras")
            editoras = cursor.fetchall()
            return render_template("cadeditora.html", editoras=editoras)
        except Exception as erro:
            return f"Erro {erro}"
        except Error as erro:
            return f"Erro BD {erro}"
        finally:
            encerrar_db(cursor, conexao)

    if request.method == 'POST':
        dados = request.get_json()
        editora = dados.get('nome_editora')
        try:
            conexao, cursor = conectar_db()
            cursor.execute("INSERT INTO editoras VALUES (null, %s)", (editora,))
            conexao.commit()
            return jsonify({'success': True}), 200
        except Exception as erro:
            return f"Erro {erro}"
        except Error as erro:
            return f"Erro BD {erro}"
        finally:
            encerrar_db(cursor, conexao)
              
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)