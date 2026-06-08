from flask import request
from flask_restx import Namespace, Resource, fields
from flask_login import login_user, logout_user, login_required
from service.user_service import UserService

auth_ns = Namespace('auth', description='Autenticação e Sessão')
user_service = UserService()

# Modelo de payload para o Swagger documentar os campos
login_model = auth_ns.model('LoginInput', {
    'email': fields.String(required=True, description='E-mail de acesso'),
    'password': fields.String(required=True, description='Senha do usuário')
})

@auth_ns.route('/login')
class Login(Resource):
    
    @auth_ns.expect(login_model, validate=True)
    def post(self):
        """Efetua o login e gera o cookie de sessão"""
        dados = auth_ns.payload
        
        # 1. Busca o usuário
        usuario = user_service.select_user_by_email(dados['email'])
        
        # 2. Valida as credenciais (Obs: Em produção, use check_password_hash)
        if not usuario or usuario.password != dados['password']:
            auth_ns.abort(401, "E-mail ou senha incorretos.")
            
        # 3. Dispara o mecanismo do Flask-Login para salvar a sessão no navegador
        login_user(usuario)
        
        return {
            "message": f"Login efetuado com sucesso! Bem-vindo(a), {usuario.name}.",
            "user_id": usuario.id,
            "role": usuario.role
        }, 200


@auth_ns.route('/logout')
class Logout(Resource):
    
    def post(self):
        """Encerra a sessão ativa (limpa o cookie)"""
        logout_user()  # Destrói o cookie de sessão do lado do cliente
        return {"message": "Sessão encerrada com sucesso."}, 200
