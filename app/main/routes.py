from db_functions import *
from flask import Blueprint, render_template, redirect, session, request

main = Blueprint('main', __name__)


@main.route('/')
def index():
    logado = session.get('logado', False)
    return render_template('index.html', titulo="Verbum - Reserva de livros", logado=logado)

@main.route('/login')
def login():
    return render_template('login.html', titulo="Verbum - Login")

@main.route('/contato')
def contato():
    nome_usuario = session.get('nome', "")
    logado = session.get('logado', True)
    return render_template('contato.html', logado=logado, titulo="Verbum - Contato", nome_usuario=nome_usuario)

@main.route('/adm')
def adm():
    logado = session.get('logado', True)
    return render_template('adm_index.html', logado=logado, titulo="Verbum ADM - Home ")

@main.route('/redirecionar')
def redirecionar():
    nivel_usuario = session.get('admin', 'usuario')
    
    if nivel_usuario == 'admin':
        return redirect('/adm')
    elif nivel_usuario == 'usuario':
        return redirect('/home')
    else:
        return redirect('/')
    
@main.route('/login', methods=['POST'])
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
    
    if senha == senha_db:
        idUsuario = usuario['idUsuario']
        nome = usuario['nome']
        senha_db = usuario['senha']
        session['logado'] = True
        session['idUsuario'] = idUsuario
        session['nome'] = nome
        session['nivelUsuario'] = 'usuario'
        return redirect('/home')
    else:
        return render_template("login.html", msg="Senha incorreta!")
    
@main.route('/logout')
def logout():
    session.clear()
    return redirect('/')