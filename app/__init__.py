from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__, template_folder='../templates')
    CORS(app)
    app.secret_key = 'verbum'

    from app.main.routes import main as main_blueprint
    from app.livro.routes import livro as livro_blueprint
    from app.usuario.routes import usuario as usuario_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(livro_blueprint)
    app.register_blueprint(usuario_blueprint)

    return app
