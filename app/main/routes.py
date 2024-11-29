from db_functions import *
from flask import Blueprint, render_template, redirect, session, request, jsonify, flash

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
    logado = session.get('logado', False)
    nivel_usuario = session.get('nivelUsuario', None)
    nome_usuario = session.get('nome', "")

    if nivel_usuario == 'admin':
        logado = session.get('logado', True)

    return render_template('contato.html', logado=logado, titulo="Verbum - Contato", nome_usuario=nome_usuario, nivel_usuario=nivel_usuario)

@main.route('/adm')
def adm():
    logado = session.get('logado', True)
    conexao, cursor = conectar_db()

    query = """
        SELECT 
            livros.titulo AS titulo_livro,
            a.nome,
            a.serie,
            le.idLivro AS id_livro,
            le.idUsuario AS id_usuario
        FROM listaespera le
        INNER JOIN Livros ON le.idLivro = livros.idLivro
        INNER JOIN Usuarios a ON le.idUsuario = a.idUsuario
        WHERE le.idUsuario = (
            SELECT le.idUsuario
            FROM listaespera le1
            WHERE le1.idLivro = le.idLivro AND le1.status = 1
            ORDER BY le1.dataReserva ASC
            LIMIT 1
        )
    """
    cursor.execute(query)
    usuarios = cursor.fetchall()

    encerrar_db(conexao, cursor)
    return render_template('adm_index.html', logado=logado, titulo="Verbum ADM - Home", usuarios=usuarios)


@main.route('/emprestimo', methods=['POST'])
def fazer_emprestimo():
    id_livro = request.form.get('id_livro')
    id_usuario = request.form.get('id_usuario')

    conexao, cursor = conectar_db()
    
    try:
        cursor.execute("""
        INSERT INTO Emprestimos (idLivro, idUsuario, dataEmprestimo, dataDevolucao) 
        VALUES (%s, %s, NOW(), DATE_ADD(NOW(), INTERVAL 30 DAY))
    """, (id_livro, id_usuario))
        print("Empréstimo registrado com sucesso.")
        
        cursor.execute("""
            DELETE FROM listaespera
            WHERE idLivro = %s AND idUsuario = %s
        """, (id_livro, id_usuario))
        print("Registro removido da lista de espera.")
        
        conexao.commit()
        flash("Empréstimo realizado com sucesso!", "success")
    except Exception as e:
        conexao.rollback()
        print(f"Erro ao realizar empréstimo: {str(e)}")
        flash(f"Erro ao realizar empréstimo: {str(e)}", "danger")
    finally:
        cursor.close()
        conexao.close()
    
    return redirect('/adm')

@main.route('/redirecionar')
def redirecionar():
    nivel_usuario = session.get('nivelUsuario', None)

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
    
    if usuario:
        senha_db = usuario['senha']

        if senha == senha_db:
            idUsuario = usuario['idUsuario']
            nome = usuario['nome']
            
            session['logado'] = True
            session['idUsuario'] = idUsuario
            session['nome'] = nome
            session['nivelUsuario'] = 'usuario'
            return redirect('/home')
        else:
            return render_template("login.html", msg="Senha incorreta!")
    else:
        return render_template("login.html", msg="Usuário não encontrado!")

@main.route('/logout')
def logout():
    session.clear()
    return redirect('/')