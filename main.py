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

# @app.route('/adicionar_livro', methods=['GET', 'POST'])
# def adicionar_livro():
#     if request.method == 'POST':
#         titulo = request.form['titulo']
#         autor = request.form['autor']
#         editora = request.form['editora']
#         ano_publicacao = request.form['ano']
#         quantidade = request.form['quantidade']
#         categoria = request.form['categoria']
#         # Lê a imagem como binário
#         imagem_capa = request.files['imagem'].read()

#         cursor = db.cursor()
#         sql = """INSERT INTO Livro (idAutor, idEditora, titulo, anoPublicacao, quantidade, categoria, imagemCapa)
#                  VALUES (%s, %s, %s, %s, %s, %s, %s)"""
#         valores = (autor, editora, titulo, ano_publicacao,
#                    quantidade, categoria, imagem_capa)
#         cursor.execute(sql, valores)
#         db.commit()

#         return 'Livro adicionado com sucesso!'

#     return render_template('index.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    logado = session.get('logado', False)
    return render_template('index.html', logado=logado)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/recuperarsenha')
def recuperarsenha():
    return render_template('recuperarsenha.html')

@app.route('/livros')
def livros():
    return render_template('livros.html')

@app.route('/contato')
def contato():
    return render_template('contato.html')

@app.route('/modelo')
def modelo():
    logado = session.get('logado', True)
    return render_template('modelo.html', logado=logado)

@app.route('/login', methods=['POST'])
def logar():
    email = request.form['email']
    senha = request.form['senha']

    if email == 'admin@gmail.com' and senha == '123':
        session['logado'] = True  # Armazena o estado de login na sessão
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