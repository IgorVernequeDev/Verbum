from db_functions import *
from flask import Blueprint, render_template, request, redirect, session

usuario = Blueprint('usuario', __name__)

@usuario.route('/home')
def home():
    nome_usuario = session.get('nome', "")
    logado = session.get('logado', True)

    conexao, cursor = conectar_db()

    encerrar_db(cursor, conexao)

    return render_template('index.html', logado=logado, nome_usuario=nome_usuario, titulo="Verbum - Home")

@usuario.route('/cadaluno', methods=['POST'])
def cadaluno():
    conexao, cursor = conectar_db()

    nome = request.form['nome']
    email = request.form['email']
    serie = request.form['serie']
    letra = request.form['letra']
    senha = request.form['senha']
    confirmasenha = request.form['confirmasenha']

    serie = serie + ' ' + letra

    
    if senha == confirmasenha:
        
        cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
        user = cursor.fetchone()

        if user:
            
            return render_template("cadaluno.html", msg="Este email já está cadastrado!", 
                                   nome=nome, email=email, serie=serie, letra=letra)

      
        cursor.execute(
            'INSERT INTO usuarios (nome, email, serie, senha) VALUES (%s, %s, %s, %s)', 
            (nome, email, serie, senha)
        )
        conexao.commit()
        conexao.close()
        return redirect('/adm')

    else:
        return render_template("cadaluno.html", msg="As senhas não se coincidem!", 
                               nome=nome, email=email, serie=serie, letra=letra)    

@usuario.route('/cadastraraluno')
def cadastraraluno():
    logado = session.get('logado', True)
    return render_template('cadaluno.html', logado=logado, titulo="Verbum - Cadastro de aluno")


@usuario.route('/livrosReservados')
def livrosReservados():
    nome_usuario = session.get('nome', "")
    logado = session.get('logado', True)
    return render_template('livrosReservados.html', logado=logado, titulo="Verbum - Livros reservados", nome_usuario=nome_usuario)