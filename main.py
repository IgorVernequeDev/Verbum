from flask import Flask, render_template, redirect, request, session
import mysql.connector  
from flask_cors import CORS
from db_functions import *

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
    return render_template('contato.html', logado=logado,titulo="Verbum - Contato")

@app.route('/livrosReservados')
def livrosReservados():
    logado = session.get('logado', False) 
    return render_template('livrosReservados.html', logado=logado,titulo="Verbum - Contato")

@app.route('/modelo')
def modelo():
    logado = session.get('logado', True)
    return render_template('modelo.html', logado=logado)

@app.route('/adm')
def adm():
    logado = session.get('logado', True)
    return render_template('adm_index.html', logado=logado, titulo="Verbum ADM - Home ")

@app.route('/cadlivro')
def cadlivro():
    logado = session.get('logado', True) 
    return render_template('cadlivro.html', logado=logado, titulo="Verbum ADM - Cadastro")

@app.route('/adm_listadeespera')
def listadeespera():
    logado = session.get('logado', True)
    return render_template('adm_listadeespera.html', logado = logado, titulo="Verbum ADM - Cadastro")

@app.route('/informacoespessoais')
def informacoespessoais():
    logado = session.get('logado', True)
    return render_template('informacoespessoais.html', logado = logado, titulo="Verbum ADM - Cadastro")

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
        return render_template("login.html",msg="Usuário/Senha estão incorretos!")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)