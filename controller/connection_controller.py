from flask_restx import Resource, Namespace, fields
from service.connection_service import ConnectionService
from model.connection import Connection
from util.auth_role_enum_util import roles_required, UserRole
from flask_login import current_user

connection_ns = Namespace("connection", description="Operações CRUD de Conexões de Rede")
connection_service = ConnectionService()

connection_model = connection_ns.model('ConnectionModel', {
    'id': fields.Integer(readonly=True, description='Identificador único da conexão física/lógica'),
    'type': fields.String(required=True, description='Tipo de conexão (Ex: Fibra, Cabo UTP, Wi-Fi, VPN)'),
    'source_id': fields.Integer(required=True, description='ID do dispositivo de origem (Source Device)'),
    'destination_id': fields.Integer(required=True, description='ID do dispositivo de destino (Destination Device)')
})


@connection_ns.route('/')
class ConnectionList(Resource):

    @connection_ns.doc("list_connections")
    @connection_ns.marshal_list_with(connection_model)
    @roles_required(UserRole.USER, UserRole.TI, UserRole.ADM) # Todos os autenticados podem ver o mapa de rede
    def get(self):
        """[READ] Lista todos os elos e conexões de rede do inventário"""
        return connection_service.list_connection()

    @connection_ns.doc("create_connection")
    @connection_ns.expect(connection_model, validate=True)
    @connection_ns.marshal_with(connection_model, code=201)
    @roles_required(UserRole.TI, UserRole.ADM) 
    def post(self):
        """[CREATE] Cadastra um novo elo de conexão entre dois dispositivos"""
        dados = connection_ns.payload
        
        nova_connection = Connection(
            type=dados['type'],
            source_id=dados['source_id'],
            destination_id=dados['destination_id']
        )
        
        return connection_service.create_connection(nova_connection, current_user.id), 201


@connection_ns.route('/<int:id>')
@connection_ns.param('id', 'O identificador numérico da conexão')
class ConnectionDetail(Resource):

    @connection_ns.doc("get_connection")
    @connection_ns.marshal_with(connection_model)
    @roles_required(UserRole.USER, UserRole.TI, UserRole.ADM)
    def get(self, id):
        """[READ] Busca detalhes de uma conexão de rede específica por ID"""
        conexao = connection_service.select_connection(id)
        if not conexao:
            connection_ns.abort(404, f"Conexão com ID {id} não encontrada.")
        return conexao

    @connection_ns.doc("update_connection")
    @connection_ns.expect(connection_model, validate=True)
    @connection_ns.marshal_with(connection_model)
    @roles_required(UserRole.TI, UserRole.ADM) 
    def put(self, id):
        """[UPDATE] Atualiza os dados de uma conexão existente"""
        dados = connection_ns.payload
        
        conn_atualizada = Connection(
            id=id,
            type=dados.get('type'),
            source_id=dados.get('source_id'),
            destination_id=dados.get('destination_id')
        )
        
        try:
            return connection_service.update_connection(conn_atualizada, current_user.id), 200
        except ValueError as e:
            connection_ns.abort(404, str(e))

    @connection_ns.doc("delete_connection")
    @connection_ns.response(204, 'Conexão deletada')
    @roles_required(UserRole.ADM)
    def delete(self, id):
        """[DELETE] Remove permanentemente um elo de conexão do inventário"""
        try:
            connection_service.delete_connection(id, current_user.id)
            return '', 204
        except ValueError as e:
            connection_ns.abort(404, str(e))