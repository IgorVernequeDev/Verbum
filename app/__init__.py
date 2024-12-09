from flask import Flask
from flask_cors import CORS
from flask_caching import Cache

def create_app():
    app = Flask(__name__, template_folder='../templates')
    CORS(app)
    app.secret_key = 'verbum'

    # Configurando o cache
    app.config['CACHE_TYPE'] = 'SimpleCache'  # Cache em memória
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # Cache expira em 5 minutos
    cache = Cache(app)  # Criando o objeto de cache

    from app.main.routes import main as main_blueprint
    from app.livro.routes import livro as livro_blueprint
    from app.usuario.routes import usuario as usuario_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(livro_blueprint)
    app.register_blueprint(usuario_blueprint)

    return app
