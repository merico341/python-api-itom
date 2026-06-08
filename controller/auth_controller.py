from flask import request
from datetime import datetime
from flask_restx import Namespace, Resource, fields
from flask_login import login_user, logout_user, current_user, login_required
from service.user_service import UserService
from service.log_service import LogService, Log
from util.log_enum_util import LogOperation, LogStatus

auth_ns = Namespace('auth', description='Autenticação e Sessão')
user_service = UserService()

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
        
        usuario = user_service.select_user_by_email(dados['email'])
        
        if not usuario or usuario.password != dados['password']:
            LogService.create_log(Log(
                operation=LogOperation.LOGIN,
                status=LogStatus.WARNING,
                description='senha ou login incorretos',
                device_id=None,
                user_id=0,
                date_hour=datetime.now()
            ))
            auth_ns.abort(401, "E-mail ou senha incorretos.")
            
        login_user(usuario)

        log = Log(
            operation=LogOperation.LOGIN,
            status=LogStatus.SUCCESS,
            description='usuario_logado_com_sucesso',
            device_id=None,
            user_id=usuario.id,
            date_hour=datetime.now()
        )

        LogService.create_log(log)
        
        return {
            "message": f"Login efetuado com sucesso! Bem-vindo(a), {usuario.name}.",
            "user_id": usuario.id,
            "role": usuario.role
        }, 200


@auth_ns.route('/logout')
class Logout(Resource):
    def post(self):
        """Encerra a sessão ativa (limpa o cookie)"""
        logout_user()
        return {"message": "Sessão encerrada com sucesso."}, 200
