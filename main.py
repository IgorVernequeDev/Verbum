from flask import Flask, render_template, redirect, request, session
from flask_cors import CORS
from db_functions import conectar_db, encerrar_db
import uuid

app = Flask(__name__)
CORS(app)
app.secret_key = 'verbum'

app.config['DEBUG'] = True


@app.route('/')
def index():
    return render_template('index.html', titulo="Verbum - Lista de Espera")


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
    cursor.execute("SELECT * FROM livros WHERE idLivro = %s", (id,))
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
    return render_template('livrosReservados.html', logado=logado, titulo="Verbum - Contato")


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
    return render_template('cadastrolivro.html', logado=logado, titulo="Verbum ADM - Cadastro")


@app.route('/adm_listadeespera')
def listadeespera():
    logado = session.get('logado', True)
    return render_template('adm_listadeespera.html', logado=logado, titulo="Verbum ADM - Cadastro")


@app.route('/informacoespessoais')
def informacoespessoais():
    logado = session.get('logado', True)
    return render_template('informacoespessoais.html', logado=logado, titulo="Verbum ADM - Cadastro")


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
    imagemCapa = request.files['imagemCapa']
    editora = request.form['editora']
    anoPublicacao = request.form['anoPublicacao']
    quantidade = request.form['quantidade']

    # Gerar nome único para a imagem
    id_foto = str(uuid.uuid4().hex)
    filename = id_foto + titulo + '.png'
    
    # Salvar a imagem no diretório
    imagemCapa.save("static/img/livros/" + filename)

    cursor.execute('INSERT INTO livros (titulo, descricao, numero_paginas, genero, imagemCapa, anoPublicacao, quantidade) VALUES (%s, %s, %s, %s, %s, %s, %s)', (titulo, descricao, numero_paginas, genero, filename, anoPublicacao, quantidade))

    cursor.execute('INSERT INTO editora (nomeEditora) VALUES (%s)', (editora,))
    
    # Confirmar e fechar a conexão
    conexao.commit()
    conexao.close()

    return render_template('adm_index.html')



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
