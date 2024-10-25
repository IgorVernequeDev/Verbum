from db_functions import conectar_db, encerrar_db
from routes import *
from mysql.connector import Error
import uuid

@app.route('/livros') 
def livros():
    logado = session.get('logado', False)
    conexao, cursor = conectar_db()
    cursor.execute("SELECT * FROM livros")
    livros = cursor.fetchall()
    encerrar_db(cursor, conexao)
    return render_template('livros.html', logado=logado, titulo="Verbum - Livros", livros=livros)

@app.route('/livro/<int:id>')
def livro(id):
    logado = session.get('logado', False)
    conexao, cursor = conectar_db()
    cursor.execute("""
        SELECT livros.*, autor.nomeAutor, editora.nomeEditora
        FROM livros
        JOIN autor ON livros.idAutor = autor.idAutor
        JOIN editora ON livros.idEditora = editora.idEditora
        WHERE livros.idLivro = %s
    """, (id,))
    livro = cursor.fetchone()
    encerrar_db(cursor, conexao)
    return render_template('verlivro.html', logado=logado, titulo="Verbum - Livros", livro=livro)

@app.route('/cadastrarlivro')
def cadastrarlivro():
    logado = session.get('logado', True)
    try:
        conexao, cursor = conectar_db()
        cursor.execute("SELECT * from editora")
        editoras = cursor.fetchall()
        cursor.execute("SELECT * from autor")
        autores = cursor.fetchall()

        return render_template('cadlivro.html', editoras=editoras, autores=autores,logado=logado, titulo="Verbum ADM - Cadastro de livros")
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

    query = "SELECT idUsuario, nome, email, senha FROM usuario WHERE email = %s"
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
            session['nivelUsuario'] = 'usuario'
            return redirect('/home')
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
    idEditora = request.form['editora']
    anoPublicacao = request.form['anoPublicacao']
    quantidade = request.form['quantidade']
    idAutor = request.form['autor']

    id_foto = str(uuid.uuid4().hex)
    filename = id_foto + titulo + '.png'
    
    imagemCapa.save("static/img/livros/" + filename)

    cursor.execute('INSERT INTO livros (idAutor, idEditora, titulo, descricao, numero_paginas, genero, imagemCapa, anoPublicacao, quantidade) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (idAutor, idEditora, titulo, descricao, numero_paginas, genero, filename, anoPublicacao, quantidade))
    
    conexao.commit()
    conexao.close()

    return render_template('adm_index.html')

@app.route('/cadaluno', methods=['POST'])
def cadaluno():
    conexao, cursor = conectar_db()

    nome = request.form['nome']
    nome = nome.title()
    email = request.form['email']
    senha = request.form['senha']
    confirmasenha = request.form['confirmasenha']

    if senha == confirmasenha:
        cursor.execute('INSERT INTO usuario (nome, email, senha) VALUES (%s, %s, %s)', (nome, email, senha))
        conexao.commit()
        conexao.close()

    else:
        return render_template("cadaluno.html", msg="As senhas não se coincidem!")

    return render_template('adm_index.html')

@app.route('/cadautor', methods=['GET', 'POST'])
def cadautor():
    if request.method == 'GET':
        try:
            conexao, cursor = conectar_db()
            cursor.execute("SELECT * from autor")
            autores = cursor.fetchall()
            return render_template("cadautor.html", autores=autores)
        except Exception as erro:
            return f"Erro {erro}"
        except Error as erro:
            return f"Erro BD {erro}"
        finally:
            encerrar_db(cursor, conexao)

    if request.method == 'POST':
        autor = request.form['autor']
        try:
            conexao, cursor = conectar_db()
            cursor.execute("INSERT INTO autor VALUES (null, %s)", (autor,))
            conexao.commit()
            return redirect ('/cadastrarlivro')
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
            cursor.execute("SELECT * from editora")
            editoras = cursor.fetchall()
            return render_template("cadeditora.html", editoras=editoras)
        except Exception as erro:
            return f"Erro {erro}"
        except Error as erro:
            return f"Erro BD {erro}"
        finally:
            encerrar_db(cursor, conexao)

    if request.method == 'POST':
        editora = request.form['editora']
        try:
            conexao, cursor = conectar_db()
            cursor.execute("INSERT INTO editora VALUES (null, %s)", (editora,))
            conexao.commit()
            return redirect ('/cadastrarlivro')
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
                SELECT livros.*, autor.nomeAutor, editora.nomeEditora
                FROM livros
                JOIN autor ON livros.idAutor = autor.idAutor
                JOIN editora ON livros.idEditora = editora.idEditora
                WHERE livros.idLivro = %s
            """, (id,))
            
            livro = cursor.fetchone()
            
            cursor.execute("SELECT * FROM autor")
            autores = cursor.fetchall()

            cursor.execute("SELECT * FROM editora")
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
    app.run(debug=True)