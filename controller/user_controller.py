from flask_restx import Resource, Namespace, fields, marshal
from service.user_service import UserService
from model.user import User
from util.auth_role_enum_util import roles_required, UserRole
from flask_login import current_user

# 1. Definição do Namespace
user_ns = Namespace("user", description="Operações CRUD de Usuários")
user_service = UserService()

# 2. MODELO COMPLETO (TI e ADM veem tudo, incluindo ID e Senha)
user_model = user_ns.model('UserModel', {
    'id': fields.Integer(readonly=True, description='Identificador único'),
    'name': fields.String(required=True, description='Nome do usuário'),
    'email': fields.String(required=True, description='E-mail do usuário'),
    'password': fields.String(required=True, description='Senha'),
    'role': fields.String(default="USER", description='Papel do usuário (USER, TI, ADM)')
})

# 3. MODELO PÚBLICO RESUMIDO (O que o USER comum tem permissão para ver)
user_public_model = user_ns.model('UserPublicModel', {
    'name': fields.String(description='Nome do usuário'),
    'email': fields.String(description='E-mail do usuário'),
    'role': fields.String(description='Papel do usuário')
})


@user_ns.route('/')
class UserList(Resource):

    @user_ns.doc("list_users")
    # ATENÇÃO: Removemos o @user_ns.marshal_list_with fixo daqui de cima,
    # porque a filtragem agora vai acontecer dinamicamente lá dentro!
    def get(self):
        """[READ] Lista usuários adaptando os campos visíveis conforme a permissão"""
        
        # Garante que pelo menos o usuário esteja logado
        if not current_user.is_authenticated:
            user_ns.abort(401, "Não autenticado.")

        lista_bruta = user_service.list_users()

        # CASO 1: Se for ADM ou TI, aplica o filtro do modelo COMPLETO
        if current_user.role.upper() != "USER":
            return marshal(lista_bruta, user_model), 200
        
        # CASO 2: Se for um USER comum, aplica o filtro do modelo PÚBLICO (Esconde ID e Password)
        return marshal(lista_bruta, user_public_model), 200

    @user_ns.doc("create_user")
    @user_ns.expect(user_model, validate=True)
    @user_ns.marshal_with(user_model, code=201)
    @roles_required(UserRole.ADM)
    def post(self):
        """[CREATE] Cadastra um novo usuário no sistema (Apenas ADM)"""
        dados = user_ns.payload
        
        novo_user = User(
            name=dados['name'],
            email=dados['email'],
            password=dados['password'],
            role=dados.get('role', 'USER').upper()
        )
        return user_service.create_user(novo_user), 201


@user_ns.route('/<int:id>')
@user_ns.param('id', 'O identificador numérico do usuário')
class UserDetail(Resource):

    @user_ns.doc("get_user")
    @user_ns.marshal_with(user_model)
    @roles_required(UserRole.TI, UserRole.ADM)
    def get(self, id):
        """[READ] Busca detalhes de um usuário específico por ID"""
        usuario = user_service.select_user(id)
        if not usuario:
            user_ns.abort(404, f"Usuário com ID {id} não encontrado.")
        return usuario

    @user_ns.doc("update_user")
    @user_ns.expect(user_model, validate=True)
    @user_ns.marshal_with(user_model)
    @roles_required(UserRole.ADM)
    def put(self, id):
        """[UPDATE] Atualiza os dados de um usuário existente"""
        dados = user_ns.payload
        
        usuario_dados = User(
            id=id,
            name=dados.get('name'),
            email=dados.get('email'),
            password=dados.get('password'),
            role=dados.get('role')
        )
        
        try:
            return user_service.update_user(usuario_dados), 200
        except ValueError as e:
            user_ns.abort(404, str(e))

    @user_ns.doc("delete_user")
    @user_ns.response(204, 'Usuário deletado')
    @roles_required(UserRole.ADM)
    def delete(self, id):
        """[DELETE] Remove permanentemente um usuário"""
        try:
            user_service.delete_user(id)
            return '', 204
        except ValueError as e:
            user_ns.abort(404, str(e))


@user_ns.route('/perfil')
class Perfil(Resource):
    def get(self):
        """[READ]Retorna o perfil do usuário logado na sessão"""
        if current_user.is_authenticated:
            return {"nome": current_user.name, "cargo": current_user.role}, 200
        return {"erro": "Você não está logado"}, 401