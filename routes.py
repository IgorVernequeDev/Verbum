from flask import Flask, render_template, redirect, request, session
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = 'verbum'

app.config['DEBUG'] = True

@app.route('/')
def index():
    return render_template('index.html', titulo="Verbum - Reserva de livros")

@app.route('/login')
def login():
    return render_template('login.html', titulo="Verbum - Login")

@app.route('/contato')
def contato():
    nome_usuario = session.get('nome', "")
    logado = session.get('logado', True)
    return render_template('contato.html', logado=logado, titulo="Verbum - Contato", nome_usuario=nome_usuario)

@app.route('/livrosReservados')
def livrosReservados():
    nome_usuario = session.get('nome', "")
    logado = session.get('logado', True)
    return render_template('livrosReservados.html', logado=logado, titulo="Verbum - Livros reservados", nome_usuario=nome_usuario)

@app.route('/modelo')
def modelo():
    logado = session.get('logado', True)
    return render_template('modelo.html', logado=logado)

@app.route('/adm')
def adm():
    logado = session.get('logado', True)
    return render_template('adm_index.html', logado=logado, titulo="Verbum ADM - Home ")

@app.route('/redirecionar')
def redirecionar():
    logado = session.get('logado', True)
    nivel_usuario = session.get('nivelUsuario', 'usuario')

    if not logado:
        return redirect('/')
    
    if nivel_usuario == 'admin':
        return redirect('/adm')
    else:
        return redirect('/home')

@app.route('/cadastraraluno')
def cadastraraluno():
    logado = session.get('logado', True)
    return render_template('cadaluno.html', logado=logado, titulo="Verbum - Cadastro de aluno")