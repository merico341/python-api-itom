import os
import re
from flask import Flask
from flask_restx import Api
from flask_cors import CORS  
from flask_jwt_extended import JWTManager # 🔄 Trocado Flask-Login por JWT

from service.user_service import UserService

from controller.auth_controller import auth_ns
from controller.user_controller import user_ns
from controller.device_controller import device_ns
from controller.connection_controller import connection_ns
from controller.incident_controller import incident_ns
from controller.log_controller import log_ns

def create_app():
    app = Flask(__name__)

    # Como o JWT usa Headers, o CORS simplificado com "*" volta a funcionar perfeitamente!
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "*",
                re.compile(r"^https://.*\.vercel\.app$")
            ]
        }
    }, supports_credentials=True)

    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "chave_secreta_super_protegida_da_infra_123!")
    app.config['RESTX_MASK_SWAGGER'] = False  
    app.url_map.strict_slashes = False

    # 🛠️ CONFIGURAÇÃO DO JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "outra_chave_mestra_para_os_tokens_456!")
    jwt = JWTManager(app)

    print("[SISTEMA] Banco de dados inicializado com sucesso!")

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