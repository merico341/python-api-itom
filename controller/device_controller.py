from flask_restx import Resource, Namespace, fields
from service.device_service import DeviceService
from model.device import Device
from util.auth_role_enum_util import roles_required, UserRole
from flask_login import current_user

# 1. Definição do Namespace que será injetado no app.py
device_ns = Namespace("device", description="Operações CRUD de Dispositivos de Rede")
device_service = DeviceService()

# 2. Modelo estruturado para validação de entrada e formatação de saída no Swagger
device_model = device_ns.model('DeviceModel', {
    'id': fields.Integer(readonly=True, description='Identificador único do ativo'),
    'name': fields.String(required=True, description='Nome do dispositivo (Ex: Switch-Core-01)'),
    'type': fields.String(required=True, description='Tipo (ex: Servidor, Roteador, Switch, PC)'),
    'ip': fields.String(description='Endereço IP atribuído'),
    'user_id': fields.Integer(description='ID do usuário responsável pelo ativo')
})


@device_ns.route('/')
class DeviceList(Resource):

    @device_ns.doc("list_devices")
    @device_ns.marshal_list_with(device_model)
    @roles_required(UserRole.USER, UserRole.TI, UserRole.ADM)  # Todos os logados podem visualizar a topologia/inventário
    def get(self):
        """[READ] Lista todos os dispositivos de hardware cadastrados"""
        return device_service.list_devices()

    @device_ns.doc("create_device")
    @device_ns.expect(device_model, validate=True)
    @device_ns.marshal_with(device_model, code=201)
    @roles_required(UserRole.TI, UserRole.ADM)  # Apenas técnicos ou administradores inventariam hardware
    def post(self):
        """[CREATE] Cadastra um novo dispositivo de rede no inventário"""
        dados = device_ns.payload
        
        # Instanciação explícita alinhada com as correções anteriores para o SQLAlchemy Core
        novo_device = Device(
            name=dados['name'],
            type=dados['type'],
            ip=dados.get('ip'),
            user_id=dados.get('user_id')
        )
        
        # ATENÇÃO: Seu device_service.create_device precisa do user_id_executante para criar o LOG de auditoria
        return device_service.create_device(novo_device), 201


@device_ns.route('/<int:id>')
@device_ns.param('id', 'O identificador numérico do dispositivo')
class DeviceDetail(Resource):

    @device_ns.doc("get_device")
    @device_ns.marshal_with(device_model)
    @roles_required(UserRole.USER, UserRole.TI, UserRole.ADM)
    def get(self, id):
        """[READ] Busca detalhes de um dispositivo específico por ID"""
        dispositivo = device_service.select_device(id)
        if not dispositivo:
            device_ns.abort(404, f"Dispositivo com ID {id} não encontrado.")
        return dispositivo

    @device_ns.doc("update_device")
    @device_ns.expect(device_model, validate=True)
    @device_ns.marshal_with(device_model)
    @roles_required(UserRole.TI, UserRole.ADM)  # Apenas TI e ADM alteram topologia ou propriedades físicas
    def put(self, id):
        """[UPDATE] Atualiza os dados de um dispositivo existente"""
        dados = device_ns.payload
        
        device_atualizado = Device(
            id=id,
            name=dados.get('name'),
            type=dados.get('type'),
            ip=dados.get('ip'),
            user_id=dados.get('user_id')
        )
        
        try:
            # Substituído o '1' fixo pelo ID dinâmico extraído com segurança do cookie do Flask-Login
            return device_service.update_device(device_atualizado, current_user.id), 200
        except ValueError as e:
            device_ns.abort(404, str(e))

    @device_ns.doc("delete_device")
    @device_ns.response(204, 'Dispositivo removido')
    @roles_required(UserRole.ADM)  # A exclusão de um dispositivo afeta conexões de rede (Apenas ADM pode fazer)
    def delete(self, id):
        """[DELETE] Remove permanentemente um dispositivo do inventário"""
        try:
            # Substituído o '1' fixo pelo ID dinâmico do administrador para gravação correta no Log de auditoria
            device_service.delete_device(id, current_user.id)
            return '', 204
        except ValueError as e:
            device_ns.abort(404, str(e))