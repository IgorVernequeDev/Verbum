import os
from db_functions import conectar_db, encerrar_db
from routes import *
from mysql.connector import Error
import uuid
<<<<<<< HEAD
from flask import Flask, render_template, request, redirect, session, jsonify
from wtforms import Form, StringField, IntegerField, FileField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from werkzeug.utils import secure_filename
from datetime import date

UPLOAD_FOLDER = 'static/img/livros'  # Certifique-se de que esta pasta exista
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} # Define os tipos de arquivo permitidos

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
class CadLivroForm(Form):
    titulo = StringField('Título', validators=[DataRequired(), Length(min=3, max=100)])
    descricao = StringField('Descrição', validators=[DataRequired(), Length(min=10, max=500)])
    numero_paginas = IntegerField('Número de Páginas', validators=[DataRequired(), NumberRange(min=1, max=1000)])
    genero = StringField('Gênero', validators=[DataRequired(), Length(min=3, max=50)])  # Permite gêneros personalizados
    imagemCapa = FileField('Imagem de Capa', validators=[DataRequired()])
    editora = StringField('Editora', validators=[DataRequired(), Length(min=3, max=100)]) # Permite editoras personalizadas
    anoPublicacao = IntegerField('Ano de Publicação', validators=[DataRequired(), NumberRange(min=1900, max=date.today().year)]) # Ano atual + 1
    quantidade = IntegerField('Quantidade', validators=[DataRequired(), NumberRange(min=1, max=1000)])
    autor = StringField('Autor', validators=[DataRequired(), Length(min=3, max=100)]) # Permite autores personalizados
=======
from flask import jsonify
>>>>>>> d723fa55ae8c303a38164e94a29804cfe03209c1

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
    logado = session.get('logado', False)
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
    return render_template('verlivro.html', logado=logado, titulo="Verbum - Livros", livro=livro)

@app.route('/home')
def home():
    logado = session.get('logado', True)

    conexao, cursor = conectar_db() 

    encerrar_db(cursor, conexao)

    return render_template('index.html', logado=logado, titulo="Verbum - Home")

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
            session['nivelUsuario'] = 'usuario'
            return redirect('/home')
    else:
        return render_template("login.html", msg="Usuário não encontrado!")


@app.route('/cadlivro', methods=['POST'])
def cadlivro():
    conexao, cursor = conectar_db()

    form = CadLivroForm(request.form)
    if request.method == 'POST' and form.validate():
        titulo = form.titulo.data.title()
        descricao = form.descricao.data.title()
        numero_paginas = form.numero_paginas.data
        genero = form.genero.data.title()
        imagemCapa = form.imagemCapa.data
        editora = form.editora.data.title()
        anoPublicacao = form.anoPublicacao.data
        quantidade = form.quantidade.data
        autor = form.autor.data.title()
        

<<<<<<< HEAD
        if imagemCapa and allowed_file(imagemCapa.filename):
            # Gera um nome de arquivo seguro e único
            id_foto = str(uuid.uuid4().hex)
            extensao = secure_filename(imagemCapa.filename).rsplit('.', 1)[1].lower()
            filename = f"{id_foto}_{titulo}.{extensao}"


            try:
                conexao, cursor = conectar_db()

                # Primeiro, insira os dados do autor e da editora e recupere seus IDs
                cursor.execute("INSERT INTO autor (nome) VALUES (%s) ON DUPLICATE KEY UPDATE idAutor = idAutor", (autor,)) # Evita duplicatas
                cursor.execute("SELECT idAutor FROM autor WHERE nome = %s", (autor,))
                idAutor = cursor.fetchone()[0]

                cursor.execute("INSERT INTO editora (nome) VALUES (%s) ON DUPLICATE KEY UPDATE idEditora = idEditora", (editora,)) # Evita duplicatas
                cursor.execute("SELECT idEditora FROM editora WHERE nome = %s", (editora,))
                idEditora = cursor.fetchone()[0]


                # Agora insira os dados do livro com os IDs corretos
                cursor.execute('INSERT INTO livros (idAutor, idEditora, titulo, descricao, numero_paginas, genero, imagemCapa, anoPublicacao, quantidade) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (idAutor, idEditora, titulo, descricao, numero_paginas, genero, filename, anoPublicacao, quantidade))
                
                imagemCapa.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                conexao.commit()

                return render_template('adm_index.html', mensagem="Livro cadastrado com sucesso!") # Mensagem de sucesso

            except Exception as e:
                print(f"Erro ao cadastrar livro: {e}") # Log para ajudar na depuração
                conexao.rollback() # Desfaz as alterações em caso de erro
                return render_template('cad_livro.html', form=form, erro="Erro ao cadastrar livro. Por favor, tente novamente.")
            finally:
                 conexao.close()

        else:
            return render_template('cad_livro.html', form=form, erro = "Tipo de arquivo inválido. Por favor, envie um arquivo de imagem.")
=======
    id_foto = str(uuid.uuid4().hex)
    filename = id_foto + titulo + '.png'

    imagemCapa.save("static/img/livros/" + filename)
>>>>>>> d723fa55ae8c303a38164e94a29804cfe03209c1

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
<<<<<<< HEAD
=======
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

>>>>>>> d723fa55ae8c303a38164e94a29804cfe03209c1
    if request.method == 'POST':
        # código para cadastrar o novo autor
        dados = request.get_json()  # Obtém os dados JSON como um dicionário Python
        autor = dados.get('nome')  # Acessa o valor da chave 'nome'
        try:
            conexao, cursor = conectar_db()
            cursor.execute("INSERT INTO autores VALUES (null, %s)", (autor,))
            conexao.commit()
<<<<<<< HEAD
            return jsonify({'success': True}), 200
        except Exception as erro:
            return f"Erro {erro}"
        except Error as erro:
            return f"Erro BD {erro}"
        finally:
            encerrar_db(cursor, conexao)
    else:
        # código para exibir a lista de autores
        try:
            conexao, cursor = conectar_db()
            cursor.execute("SELECT * from autor")
            autores = cursor.fetchall()
            return render_template('/cadautor', autores=autores)
=======
            return redirect('/cadastrarlivro')
>>>>>>> d723fa55ae8c303a38164e94a29804cfe03209c1
        except Exception as erro:
            return f"Erro {erro}"
        except Error as erro:
            return f"Erro BD {erro}"
        finally:
            encerrar_db(cursor, conexao)

<<<<<<< HEAD
@app.route('/teste')
def teste():
    return render_template('teste.html')
=======
>>>>>>> d723fa55ae8c303a38164e94a29804cfe03209c1

@app.route('/cadeditora', methods=['GET', 'POST'])
def cadeditora():
    if request.method == 'POST':
        # código para cadastrar a nova editora
        dados = request.get_json()  # Obtém os dados JSON como um dicionário Python
        editora = dados.get('nome_editora')
        try:
            conexao, cursor = conectar_db()
            cursor.execute("INSERT INTO editora VALUES (null, %s)", (editora,))
            conexao.commit()
            return jsonify({'success': True}), 200
        except Exception as erro:
            return f"Erro {erro}"
        except Error as erro:
            return f"Erro BD {erro}"
        finally:
            encerrar_db(cursor, conexao)
    else:
        # código para exibir a lista de editoras
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
<<<<<<< HEAD
=======

    if request.method == 'POST':
        editora = request.form['editora']
        try:
            conexao, cursor = conectar_db()
            cursor.execute(
                "INSERT INTO editoras VALUES (null, %s)", (editora,))
            conexao.commit()
            return redirect('/cadastrarlivro')
        except Exception as erro:
            return f"Erro {erro}"
        except Error as erro:
            return f"Erro BD {erro}"
        finally:
            encerrar_db(cursor, conexao)

@app.route('/infpessoais')
def infpessoais():
    return render_template("infpessoais.html")


@app.route('/listaespera/<int:id>')
def listaespera(id):
    logado = session.get('logado', True)

    try:
        conexao, cursor = conectar_db()

        query_livro = "SELECT * FROM livros WHERE livros.idLivro = %s"

        query_espera = """
            SELECT usuarios.nome, usuarios.serie, reservas.dataReserva, reservas.posicaoEspera
            FROM reservas
            JOIN usuarios ON reservas.idUsuario = usuarios.idUsuario
            WHERE reservas.idLivro = %s
            ORDER BY reservas.posicaoEspera
        """

        cursor.execute(query_livro, (id,))
        livro = cursor.fetchone()

        cursor.execute(query_espera, (id,))
        lista_espera = cursor.fetchall()


        encerrar_db(cursor, conexao)

        return render_template('listaespera.html', logado=logado, titulo="Verbum - Lista de Espera", lista_espera=lista_espera, livro=livro)
    except Exception as erro:
        return f"Erro ao acessar a lista de espera: {erro}"

from flask import jsonify, request

@app.route('/reservar/<int:id>', methods=['POST'])
def reservar(id):
    try:
        id_usuario = session.get('id_usuario')
        if not id_usuario:
            return jsonify({"error": "Usuário não está logado."}), 403

        conexao, cursor = conectar_db()

        cursor.execute("SELECT quantidade FROM livros WHERE idLivro = %s", (id,))
        livro = cursor.fetchone()

        if not livro:
            encerrar_db(cursor, conexao)
            return jsonify({"error": "Livro não encontrado."}), 404

        quantidade_disponivel = livro['quantidade']
        
        if quantidade_disponivel > 0:
            cursor.execute("UPDATE livros SET quantidade = quantidade - 1 WHERE idLivro = %s", (id,))
            conexao.commit()

            cursor.execute("""
                INSERT INTO reservas (idLivro, idUsuario, dataReserva)
                VALUES (%s, %s, NOW())
            """, (id, id_usuario))
            conexao.commit()

            encerrar_db(cursor, conexao)
            return jsonify({"success": True, "message": "Livro reservado com sucesso."})

        else:
            cursor.execute("""
                SELECT MAX(posicaoEspera) FROM reservas WHERE idLivro = %s
            """, (id,))
            ultima_posicao = cursor.fetchone()[0]
            nova_posicao = ultima_posicao + 1 if ultima_posicao else 1

            cursor.execute("""
                INSERT INTO reservas (idLivro, idUsuario, dataReserva, posicaoEspera)
                VALUES (%s, %s, NOW(), %s)
            """, (id, id_usuario, nova_posicao))
            conexao.commit()

            encerrar_db(cursor, conexao)
            return jsonify({"success": True, "message": "Livro adicionado à lista de espera."})

    except Exception as erro:
        return jsonify({"error": str(erro)}), 500
     
>>>>>>> d723fa55ae8c303a38164e94a29804cfe03209c1
            
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
