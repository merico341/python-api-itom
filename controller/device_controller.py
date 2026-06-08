from flask_restx import Resource, Namespace, fields
from service.device_service import DeviceService
from model.device import Device
from util.auth_role_enum_util import roles_required, UserRole
from flask_login import current_user
from requests import request

device_ns = Namespace("device", description="Operações CRUD de Dispositivos de Rede e Integrações")
device_service = DeviceService()

# Modelo padrão para gerenciamento individual de ativos
device_model = device_ns.model('DeviceModel', {
    'id': fields.Integer(readonly=True, description='Identificador único do ativo'),
    'name': fields.String(required=True, description='Nome do dispositivo (Ex: Switch-Core-01)'),
    'type': fields.String(required=True, description='Tipo (ex: Servidor, Roteador, Switch, PC)'),
    'ip': fields.String(description='Endereço IP atribuído'),
    'user_id': fields.Integer(description='ID do usuário responsável pelo ativo')
})

# Modelo de payload para o Swagger saber o que a rota espera receber por JSON
sync_payload_model = device_ns.model('SyncPayload', {
    'className': fields.String(required=False, description='Nome da classe CMDB do ServiceNow (Ex: cmdb_ci_server, cmdb_ci_linux_server)', default='cmdb_ci_hardware')
})


@device_ns.route('/sync/servicenow')
class ServiceNowSync(Resource):
    
    @device_ns.doc("sync_servicenow_devices")
    @device_ns.expect(sync_payload_model, validate=True)
    @device_ns.response(200, "Sincronização realizada com sucesso")
    @device_ns.response(401, "Sessão inválida ou não autenticada no sistema")
    @device_ns.response(502, "Falha de Autenticação com o ServiceNow (Credenciais Inválidas / Instância Hibernando)")
    @roles_required(UserRole.TI, UserRole.ADM)
    def post(self):
        """[INTEGRATION] Sincroniza dinamicamente ativos do ServiceNow enviando a classe por JSON"""
        try:
            user_id_executante = current_user.id
            
            # 🛠️ CORREÇÃO: Captura o payload JSON utilizando a propriedade correta do Namespace
            dados = device_ns.payload if device_ns.payload else {}
            class_name = dados.get('className')  # Agora recupera sem quebrar a execução
            
            # Executa a camada de serviço
            resultado = device_service.sync_servicenow_devices(user_id_executante, class_name)
            
            return resultado, 200

        except Exception as e:
            # 🔍 Captura se o erro que subiu do service foi o 401 disparado pela API externa do ServiceNow
            erro_str = str(e)
            if "401" in erro_str:
                print(f"\n[CRÍTICO] O ServiceNow rejeitou a conexão: {erro_str}")
                print("[DICA] Verifique se as variáveis SERVICENOW_USER e SERVICENOW_PASSWORD estão corretas")
                print("[DICA] Se for uma PDI (instância de desenvolvimento), verifique se ela não entrou em hibernação.\n")
                device_ns.abort(502, f"O ServiceNow retornou 401 Unauthorized: Usuário/Senha inválidos ou Instância fora do ar.")
            
            device_ns.abort(500, f"Falha na execução do sincronismo dinâmico: {erro_str}")

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
    @roles_required(UserRole.TI, UserRole.ADM) 
    def post(self):
        """[CREATE] Cadastra um novo dispositivo de rede no inventário"""
        dados = device_ns.payload
        
        novo_device = Device(
            name=dados['name'],
            type=dados['type'],
            ip=dados.get('ip'),
            user_id=dados.get('user_id')
        )
        
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
    @roles_required(UserRole.TI, UserRole.ADM)  
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
            return device_service.update_device(device_atualizado, current_user.id), 200
        except ValueError as e:
            device_ns.abort(404, str(e))

    @device_ns.doc("delete_device")
    @device_ns.response(204, 'Dispositivo removido')
    @roles_required(UserRole.ADM)  
    def delete(self, id):
        """[DELETE] Remove permanentemente um dispositivo do inventário"""
        try:
            device_service.delete_device(id, current_user.id)
            return '', 204
        except ValueError as e:
            device_ns.abort(404, str(e))