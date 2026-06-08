from flask_restx import Resource, Namespace, fields
from service.log_service import LogService
from model.log import Log
from util.auth_role_enum_util import roles_required, UserRole

# 1. Definição do Namespace com identidade visual (Emoji)
log_ns = Namespace("log", description="Trilha de Auditoria e Logs do Sistema")
log_service = LogService()

# 2. Modelo estruturado com base EXATA no seu LogService e no banco
log_model = log_ns.model('LogModel', {
    'id': fields.Integer(readonly=True, description='Identificador único do log'),
    'operation': fields.String(required=True, description='Operação realizada (Ex: INSERT, UPDATE, LOGIN)'),
    'status': fields.String(required=True, description='Status do evento (Ex: SUCCESS, FAILED)'),
    'description': fields.String(description='Detalhamento opcional do log'),
    'device_id': fields.Integer(description='ID do dispositivo afetado (se aplicável)'),
    'user_id': fields.Integer(description='ID do usuário afetado/responsável (se aplicável)'),
    'date_hour': fields.DateTime(readonly=True, description='Data e hora exata do registro')
}, ordered=True)


@log_ns.route('/')
class LogList(Resource):

    @log_ns.doc("list_logs")
    @log_ns.marshal_list_with(log_model)
    @roles_required(UserRole.TI, UserRole.ADM)  # Apenas TI e ADM acessam a auditoria global
    def get(self):
        """[READ] Lista toda a trilha de auditoria do sistema"""
        return log_service.list_log()

@log_ns.route('/<int:id>')
@log_ns.param('id', 'O identificador numérico do log')
class LogDetail(Resource):

    @log_ns.doc("get_log")
    @log_ns.marshal_with(log_model)
    @roles_required(UserRole.TI, UserRole.ADM)
    def get(self, id):
        """[READ] Busca um log específico por ID"""
        log_registro = log_service.select_log(id)
        if not log_registro:
            log_ns.abort(404, f"Registro de log com ID {id} não encontrado.")
        return log_registro


@log_ns.route('/device/<int:device_id>')
@log_ns.param('device_id', 'O ID do dispositivo para filtrar o histórico')
class LogByDevice(Resource):

    @log_ns.doc("list_logs_by_device")
    @log_ns.marshal_list_with(log_model)
    @roles_required(UserRole.TI, UserRole.ADM)
    def get(self, device_id):
        """[READ] Filtra e lista os logs relacionados a um dispositivo específico"""
        return log_service.list_log_by_device(device_id)


@log_ns.route('/user/<int:user_id>')
@log_ns.param('user_id', 'O ID do usuário para filtrar as ações')
class LogByUser(Resource):

    @log_ns.doc("list_logs_by_user")
    @log_ns.marshal_list_with(log_model)
    @roles_required(UserRole.TI, UserRole.ADM)
    def get(self, user_id):
        """[READ] Filtra e lista as ações e eventos de um usuário específico"""
        return log_service.list_log_by_user(user_id)