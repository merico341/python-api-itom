from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from service.user_service import UserService # Ou onde você valida a senha

auth_ns = Namespace('auth', description='Operações de Autenticação')
user_service = UserService()

@auth_ns.route('/login')
class Login(Resource):
    def post(self):
        dados = request.get_json()
        email = dados.get("email")
        password = dados.get("password")

        usuario = user_service.select_user_by_email(email)
        
        if not usuario or usuario.password != password:
            auth_ns.abort(401, "E-mail ou senha incorretos.")
                    
        if not usuario:
            return {"message": "E-mail ou senha incorretos"}, 401

        # 🛠️ GERANDO O JWT TOKEN (Guardamos o ID do usuário como identidade)
        access_token = create_access_token(identity=str(usuario.id))

        return {
            "message": "Login realizado com sucesso",
            "token": access_token,
            "user": {
                "id": usuario.id,
                "name": usuario.name,
                "email": usuario.email,
                "role": usuario.role
            }
        }, 200