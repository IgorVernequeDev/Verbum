from flask import Flask, render_template, redirect, request, session
import mysql.connector  
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.secret_key = 'verbum'

# Conexão com o banco de dados
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="senai",
    database="VERBUM"
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    logado = session.get('logado', True)
    return render_template('index.html', logado=logado)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/livros')
def livros():
    logado = session.get('logado', False) 
    return render_template('livros.html', logado=logado)

@app.route('/contato')
def contato():
    logado = session.get('logado', False) 
    return render_template('contato.html', logado=logado)

@app.route('/modelo')
def modelo():
    logado = session.get('logado', True)
    return render_template('modelo.html', logado=logado)

@app.route('/adm')
def adm():
    logado = session.get('logado', True)
    return render_template('adm_index.html', logado=logado)

@app.route('/cadlivro')
def cadlivro():
    logado = session.get('logado', True) 
    return render_template('cadlivro.html', logado=logado)

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

# @app.route('/capa_livro/<int:id>')  
# def capa_livro(id):
#     cursor = db.cursor()
#     cursor.execute("SELECT imagemCapa FROM Livro WHERE idLivro = %s", (id,))
#     imagem = cursor.fetchone()[0]

#     return Response(imagem, mimetype='image/jpeg')

@app.route('/logout')
def logout():
    session.pop('logado', None)
    session.clear()
    return redirect('/home')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)