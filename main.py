import os
from db_functions import conectar_db, encerrar_db
from routes import *
from mysql.connector import Error
import uuid
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

    if email == 'admin@gmail.com' and senha == '123':
        session['logado'] = True
        session['nivelUsuario'] = 'admin'
        return redirect('/adm')
    elif email == 'aluno@gmail.com' and senha == '123':
        session['logado'] = True
        session['nivelUsuario'] = 'usuario'
        return redirect('/home')
    else:
        return render_template("login.html", msg="Usuário/Senha estão incorretos!")

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

    cursor.execute('INSERT INTO livros (idAutor, idEditora, titulo, descricao, numero_paginas, genero, imagemCapa, anoPublicacao, quantidade) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)', (idAutor, idEditora, titulo, descricao, numero_paginas, genero, filename, anoPublicacao, quantidade))
    
    conexao.commit()
    conexao.close()

    return render_template('adm_index.html')

@app.route('/cadautor', methods=['GET', 'POST'])
def cadautor():
    if request.method == 'POST':
        # código para cadastrar o novo autor
        dados = request.get_json()  # Obtém os dados JSON como um dicionário Python
        autor = dados.get('nome')  # Acessa o valor da chave 'nome'
        try:
            conexao, cursor = conectar_db()
            cursor.execute("INSERT INTO autor VALUES (null, %s)", (autor,))
            conexao.commit()
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
        except Exception as erro:
            return f"Erro {erro}"
        except Error as erro:
            return f"Erro BD {erro}"
        finally:
            encerrar_db(cursor, conexao)

@app.route('/teste')
def teste():
    return render_template('teste.html')

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
            cursor.execute("SELECT * from editora")
            editoras = cursor.fetchall()
            return render_template("cadeditora.html", editoras=editoras)
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