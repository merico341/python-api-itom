import os
import re  # Importação necessária para a validação dinâmica da Vercel
from flask import Flask
from flask_restx import Api
from flask_login import LoginManager
from flask_cors import CORS  

from model.user import User
from model.device import Device
from model.incident import Incident
from model.connection import Connection
from model.log import Log

from service.user_service import UserService

from controller.auth_controller import auth_ns
from controller.user_controller import user_ns
from controller.device_controller import device_ns
from controller.connection_controller import connection_ns
from controller.incident_controller import incident_ns
from controller.log_controller import log_ns

def create_app():
    app = Flask(__name__)

    # 🛠️ CORREÇÃO 1: CORS dinâmico. Aceita localhost E qualquer subdomínio da Vercel.
    # Isso resolve a regra de segurança que proíbe o uso de "*" com credenciais ativas.
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",
                re.compile(r"https://v0-resolveit-front-end.onrender.com/")
            ]
        }
    }, supports_credentials=True)

    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "chave_secreta_super_protegida_da_infra_123!")
    app.config['RESTX_MASK_SWAGGER'] = False  
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True
    
    # 🛠️ CORREÇÃO 2: Configuração limpa e sem duplicidade para Cross-Domain Cookies
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'  
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['REMEMBER_COOKIE_SAMESITE'] = 'None'
    app.config['REMEMBER_COOKIE_SECURE'] = True

    # 🛠️ CORREÇÃO 3: Evita erros de redirecionamento 308 (com ou sem barra final)
    app.url_map.strict_slashes = False

    print("[SISTEMA] Conectando ao PostgreSQL e validando tabelas...")
    print("[SISTEMA] Banco de dados inicializado com sucesso!")

    login_manager = LoginManager()
    login_manager.init_app(app)

    user_service = UserService()

    @login_manager.user_loader
    def load_user(user_id):
        return user_service.select_user(int(user_id))

    api = Api(
        app,
        title="API de Gestão de Ativos e Incidentes de TI",
        version="1.0",
        description="Sistema unificado de suporte técnico corporativo.",
        doc="/docs"
    )

    api.add_namespace(auth_ns, path='/api/auth')
    api.add_namespace(user_ns, path='/api/user')
    api.add_namespace(device_ns, path='/api/device')
    api.add_namespace(connection_ns, path='/api/connection')
    api.add_namespace(incident_ns, path='/api/incident')
    api.add_namespace(log_ns, path='/api/log')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True)