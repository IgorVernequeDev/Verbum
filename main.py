from flask import Flask, render_template, redirect, request, session
from flask_cors import CORS
from db_functions import conectar_db, encerrar_db
import uuid
from mysql.connector import Error

app = Flask(__name__)
CORS(app)
app.secret_key = 'verbum'

app.config['DEBUG'] = True

@app.route('/')
def index():
    return render_template('index.html', titulo="Verbum - Reserva de livros")

@app.route('/home')
def home():
    logado = session.get('logado', True)
    return render_template('index.html', logado=logado, titulo="Verbum - Home")

@app.route('/login')
def login():
    return render_template('login.html', titulo="Verbum - Login")

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


@app.route('/contato')
def contato():
    logado = session.get('logado', False)
    return render_template('contato.html', logado=logado, titulo="Verbum - Contato")

@app.route('/livrosReservados')
def livrosReservados():
    logado = session.get('logado', False)
    return render_template('livrosReservados.html', logado=logado, titulo="Verbum - Livros reservados")

@app.route('/modelo')
def modelo():
    logado = session.get('logado', True)
    return render_template('modelo.html', logado=logado)

@app.route('/adm')
def adm():
    logado = session.get('logado', True)
    return render_template('adm_index.html', logado=logado, titulo="Verbum ADM - Home ")

@app.route('/cadastrarlivro')
def cadastrarlivro():
    logado = session.get('logado', True)
    try:
        conexao, cursor = conectar_db()
        cursor.execute("SELECT * from editora")
        editoras = cursor.fetchall()
        cursor.execute("SELECT * from autor")
        autores = cursor.fetchall()

        return render_template('cadastrolivro.html', editoras=editoras, autores=autores,logado=logado, titulo="Verbum ADM - Cadastro de livros")
    except Exception as erro:
        return f"Erro {erro}"
    except Error as erro:
        return f"Erro BD {erro}"
    
    finally:
        encerrar_db(cursor, conexao)

@app.route('/adm_listadeespera')
def listadeespera():
    logado = session.get('logado', True)
    return render_template('adm_listadeespera.html', logado=logado, titulo="Verbum ADM - Lista de espera")

@app.route('/alunos')
def alunos():
    logado = session.get('logado', True)
    return render_template('alunos.html', logado=logado)

@app.route('/informacoespessoais')
def informacoespessoais():
    logado = session.get('logado', True)
    return render_template('informacoespessoais.html', logado=logado, titulo="Verbum - Informações Pessoais")

@app.route('/login', methods=['POST'])
def logar():
    email = request.form['email']
    senha = request.form['senha']

    if email == 'admin@gmail.com' and senha == '123':
        session['logado'] = True
        return redirect('/adm')
    elif email == 'aluno@gmail.com' and senha == '123':
        session['logado'] = True
        return redirect('/home')
    else:
        return render_template("login.html", msg="Usuário/Senha estão incorretos!")

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

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)