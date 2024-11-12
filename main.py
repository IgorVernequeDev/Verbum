from datetime import datetime
from db_functions import conectar_db, encerrar_db
from routes import *
from mysql.connector import Error
import uuid
from flask import render_template, request, redirect, session, jsonify

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
    if not logado:
        return redirect('/login')

    conexao, cursor = conectar_db()
    
    cursor.execute("""
        SELECT livros.*, autores.nomeAutor, editoras.nomeEditora
        FROM livros
        JOIN autores ON livros.idAutor = autores.idAutor
        JOIN editoras ON livros.idEditora = editoras.idEditora
        WHERE livros.idLivro = %s
    """, (id,))
    livro = cursor.fetchone()
    encerrar_db(cursor, conexao)
    return render_template('verlivro.html', logado=logado, titulo="Verbum - Livros", livro=livro, verlivro=True)
    
    try:
        cursor.execute("""
            SELECT livros.*, autores.nomeAutor, editoras.nomeEditora
            FROM livros
            JOIN autores ON livros.idAutor = autores.idAutor
            JOIN editoras ON livros.idEditora = editoras.idEditora
            WHERE livros.idLivro = %s
        """, (id,))
        livro = cursor.fetchone()
    finally:
        encerrar_db(cursor, conexao)

    if livro is None:
        return render_template('erro.html', mensagem="Livro não encontrado"), 404 

    return render_template('verlivro.html', logado=logado, titulo="Verbum - Livros", livro=livro)

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
        senha_db = usuario['senha']

        if senha == senha_db:
            session['logado'] = True
            session['idUsuario'] = idUsuario
            session['nome'] = nome
            session['nivelUsuario'] ='usuario'
            return redirect('/home')
        else:
            return render_template("login.html", msg="Senha incorreta!")

    else:
        return render_template("login.html", msg="Usuário não encontrado!")

@app.route('/cadlivro', methods=['POST'])
def cadlivro():
    conexao, cursor = conectar_db()

    titulo = request.form['titulo']
    titulo = titulo.title()
    descricao = request.form['descricao']
    descricao = descricao.title()
    numero_paginas = request.form['numero_paginas']
    genero = request.form['genero']
    genero = genero.title()
    imagemCapa = request.files['imagemCapa']
    anoPublicacao = request.form['anoPublicacao']
    quantidade = request.form['quantidade']
    idAutor = request.form['autor']
    idEditora = request.form['editora']

    id_foto = str(uuid.uuid4().hex)
    filename = id_foto + titulo + '.png'

    imagemCapa.save("static/img/livros/" + filename)

    cursor.execute('INSERT INTO livros (idAutor, idEditora, titulo, descricao, numero_paginas, genero, imagemCapa, anoPublicacao, quantidade) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                   (idAutor, idEditora, titulo, descricao, numero_paginas, genero, filename, anoPublicacao, quantidade))

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

@app.route('/livrosreservados')
def livros_reservados():
    # Checa se o usuário está logado
    if 'usuario_id' not in session:
        return redirect('/login')

    usuario_id = session['usuario_id']

    try:
        conexao, cursor = conectar_db()
        # Busque os livros reservados pelo usuário logado
        cursor.execute("""
            SELECT livros.id, livros.titulo, livros.autor, livros.avaliacao, livros.imagemCapa
            FROM livros
            INNER JOIN reservas ON livros.id = reservas.idLivro
            WHERE reservas.idUsuario = %s
        """, (usuario_id,))
        
        livros_reservados = cursor.fetchall()
        return render_template('livrosReservados.html', livros=livros_reservados)
    
    except Exception as erro:
        return f"Erro: {erro}"
    
    finally:
        encerrar_db(cursor, conexao)

@app.route('/listaespera/<int:id>') 
def listaespera(id):
    logado = session.get('logado', True)
    conexao, cursor = conectar_db()
    idLivro = request.get('idLivro')
    idLivro = cursor.execute("SELECT idLivro FROM Livros WHERE idLivro = %s", (idLivro,))

    try:
        cursor.execute("SELECT titulo FROM livros WHERE idLivro = %s", (id,))
        livro = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) + 1 AS posicao FROM reservas WHERE idLivro = %s", (idLivro,))

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

@app.route('/reservar', methods=['POST'])
def reservar_livro(idLivro, idUsuario):
    conexao, cursor = conectar_db()
    dataReserva = datetime.now().date()
    
    # Verifica a quantidade de exemplares disponíveis
    cursor.execute("SELECT quantidade FROM livros WHERE idLivro = %s", (idLivro,))
    quantidade_disponivel = cursor.fetchone()['quantidade']
    
    if quantidade_disponivel > 0:
        # Livro disponível, usuário pode pegar o livro emprestado
        cursor.execute("""
            INSERT INTO Emprestimos (idLivro, idUsuario, dataEmprestimo)
            VALUES (%s, %s, %s)
        """, (idLivro, idUsuario, dataReserva))
        
        # Atualiza a quantidade de exemplares
        cursor.execute("UPDATE livros SET quantidade = quantidade - 1 WHERE idLivro = %s", (idLivro,))
        
        posicao = 0  # Posição 0 indica que o usuário já possui o livro emprestado
        
    else:
        # Livro não disponível, adiciona o usuário na lista de espera
        cursor.execute("SELECT COUNT(*) + 1 AS posicao FROM reservas WHERE idLivro = %s", (idLivro,))
        posicao = cursor.fetchone()['posicao']
        
        cursor.execute("""
            INSERT INTO reservas (idLivro, idUsuario, dataReserva, posicaoEspera)
            VALUES (%s, %s, %s, %s)
        """, (idLivro, idUsuario, dataReserva, posicao))

    conexao.commit()
    encerrar_db(cursor, conexao)
    
    return posicao  # Retorna a posição do usuário na lista (0 se pegou o livro, >0 se entrou na lista de espera)

def processar_devolucao(idLivro):
    conexao, cursor = conectar_db()
    
    # Atualiza a quantidade de exemplares disponíveis
    cursor.execute("UPDATE livros SET quantidade = quantidade + 1 WHERE idLivro = %s", (idLivro,))
    
    # Verifica se há alguém na lista de espera
    cursor.execute("""
        SELECT idUsuario FROM reservas
        WHERE idLivro = %s
        ORDER BY posicaoEspera
        LIMIT 1
    """, (idLivro,))
    proximo_usuario = cursor.fetchone()
    
    if proximo_usuario:
        # Move o próximo usuário na lista de espera para a tabela de empréstimos
        cursor.execute("""
            INSERT INTO Emprestimos (idLivro, idUsuario, dataEmprestimo)
            VALUES (%s, %s, %s)
        """, (idLivro, proximo_usuario['idUsuario'], datetime.now().date()))
        
        # Remove o usuário da lista de espera
        cursor.execute("DELETE FROM reservas WHERE idLivro = %s AND idUsuario = %s", (idLivro, proximo_usuario['idUsuario']))

    conexao.commit()
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

        novo_autor = request.form.get('novoAutor')
        nova_editora = request.form.get('novaEditora')

        if novo_autor:
            # Cadastra o novo autor
            cursor.execute("INSERT INTO autores (nomeAutor) VALUES (%s)", (novo_autor,))
            conexao.commit()
            id_autor = cursor.lastrowid

        if nova_editora:
            # Cadastra a nova editora
            cursor.execute("INSERT INTO editoras (nomeEditora) VALUES (%s)", (nova_editora,))
            conexao.commit()
            id_editora = cursor.lastrowid

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