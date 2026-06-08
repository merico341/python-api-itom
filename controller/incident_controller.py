from flask_restx import Resource, Namespace, fields
from service.incident_service import IncidentService
from model.incident import Incident
from util.auth_role_enum_util import roles_required, UserRole
from flask_login import current_user

incident_ns = Namespace("incident", description="Operações CRUD de Incidentes/Chamados")
incident_service = IncidentService()

incident_model = incident_ns.model('IncidentModel', {
    'id': fields.Integer(readonly=True, description='Identificador único no banco'),
    'number': fields.String(readonly=True, description='Número de protocolo único gerado pelo sistema (Ex: INC00001)'),
    'title': fields.String(required=True, description='Título curto do problema (Ex: Monitor sem sinal)'),
    'state': fields.String(default="New", description='Estado atual (New, In Progress, Resolved, Closed)'),
    'priority': fields.String(default="4 - Low", description='Nível de impacto e urgência (1 - Critical a 4 - Low)'),
    'caller_id': fields.Integer(required=True, description='ID do usuário que solicitou a abertura do chamado'),
    'description': fields.String(description='Detalhamento completo do erro ou solicitação'),
    'device_id': fields.Integer(description='ID do hardware afetado vinculado ao inventário (opcional)'),
    'created_at': fields.DateTime(readonly=True, description='Data e hora de abertura'),
    'updated_at': fields.DateTime(readonly=True, description='Data e hora da última modificação')
})


@incident_ns.route('/')
class IncidentList(Resource):

    @incident_ns.doc("list_incidents")
    @incident_ns.marshal_list_with(incident_model)
    @roles_required(UserRole.USER, UserRole.TI, UserRole.ADM)
    def get(self):
        """[READ] Lista todos os incidentes/chamados abertos e fechados"""
        return incident_service.list_incident()

    @incident_ns.doc("create_incident")
    @incident_ns.expect(incident_model, validate=True)
    @incident_ns.marshal_with(incident_model, code=201)
    @roles_required(UserRole.USER, UserRole.TI, UserRole.ADM)
    def post(self):
        """[CREATE] Abre um novo incidente no suporte técnico"""
        dados = incident_ns.payload
        
        novo_incident = Incident(
            title=dados['title'],
            state=dados.get('state', 'New'),
            priority=dados.get('priority', '4 - Low'),
            caller_id=dados['caller_id'],
            description=dados.get('description'),
            device_id=dados.get('device_id')
        )
        
        return incident_service.create_incident(novo_incident), 201


@incident_ns.route('/<int:id>')
@incident_ns.param('id', 'O identificador numérico do incidente')
class IncidentDetail(Resource):

    @incident_ns.doc("get_incident")
    @incident_ns.marshal_with(incident_model)
    @roles_required(UserRole.USER, UserRole.TI, UserRole.ADM)
    def get(self, id):
        """[READ] Busca os detalhes de um incidente específico por ID"""
        chamado = incident_service.select_incident(id)
        if not chamado:
            incident_ns.abort(404, f"Incidente com ID {id} não encontrado.")
        return chamado

    @incident_ns.doc("update_incident")
    @incident_ns.expect(incident_model, validate=True)
    @incident_ns.marshal_with(incident_model)
    @roles_required(UserRole.TI, UserRole.ADM) 
    def put(self, id):
        """[UPDATE] Atualiza o progresso, estado ou prioridade de um incidente"""
        dados = incident_ns.payload
        
        incident_atualizado = Incident(
            id=id,
            title=dados.get('title'),
            state=dados.get('state'),
            priority=dados.get('priority'),
            caller_id=dados.get('caller_id'),
            description=dados.get('description'),
            device_id=dados.get('device_id')
        )
        
        try:
            return incident_service.update_incident(incident_atualizado, current_user.id), 200
        except ValueError as e:
            incident_ns.abort(404, str(e))

    @incident_ns.doc("delete_incident")
    @incident_ns.response(204, 'Incidente excluído')
    @roles_required(UserRole.ADM)  
    def delete(self, id):
        """[DELETE] Remove permanentemente um incidente (Apenas ADM)"""
        try:
            incident_service.delete_incident(id, current_user.id)
            return '', 204
        except ValueError as e:
            incident_ns.abort(404, str(e))