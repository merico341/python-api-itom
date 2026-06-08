from enum import Enum
from functools import wraps
from datetime import datetime
from flask import abort, request
from flask_login import current_user
from model.log import Log
from service.log_service import LogService
from util.log_enum_util import LogOperation, LogStatus

class UserRole(Enum):
    USER = "USER"   # Usuário comum / Solicitante de chamados
    TI = "TI"       # Técnico / Analista de TI (Gerencia incidentes e redes)
    ADM = "ADM"     # Administrador do Sistema (Acesso total e exclusões)


def roles_required(*roles: UserRole):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Instancia o serviço de log dinamicamente para evitar importação circular
            log_service = LogService()
            
            # Captura informações contextuais da requisição HTTP atual
            rota_acessada = request.path

            # -------------------------------------------------------------
            # 1. VALIDAÇÃO: Usuário nem sequer está logado
            # -------------------------------------------------------------
            if not current_user.is_authenticated:
                # Como não sabemos quem é o usuário (não está logado), salvamos com user_id=None
                log_service.create_log(Log(
                    operation=LogOperation.CONNECT,
                    status=LogStatus.FAILED,
                    description=f"Tentativa de acesso anônimo bloqueada na rota: {rota_acessada}",
                    device_id=None,
                    user_id=0,
                    date_hour=datetime.now()
                ))
                abort(401, description="Não autenticado. Por favor, faça login para acessar este recurso.")
            
            # -------------------------------------------------------------
            # 2. VALIDAÇÃO: Cargo corrompido ou não mapeado no Enum
            # -------------------------------------------------------------
            try:
                # Verifica se a propriedade do banco/sessão bate com uma das chaves do Enum
                role_atual_usuario = current_user.role
                if isinstance(role_atual_usuario, Enum):
                    user_role_enum = role_atual_usuario
                else:
                    user_role_enum = UserRole[str(role_atual_usuario).upper()]
            except (KeyError, AttributeError):
                log_service.create_log(Log(
                    operation=LogOperation.CONNECT,
                    status=LogStatus.FAILED,
                    description=f"Usuário {current_user.name} (ID: {current_user.id}) possui um cargo inválido no banco de dados.",
                    device_id=None,
                    user_id=current_user.id,
                    date_hour=datetime.now()
                ))
                abort(403, description="Acesso negado. Seu nível de acesso não foi reconhecido pelo sistema.")
            
            # -------------------------------------------------------------
            # 3. VALIDAÇÃO: Usuário logado tentou acessar algo acima do seu nível
            # -------------------------------------------------------------
            if user_role_enum not in roles:
                permissoes_necessarias = [r.value for r in roles]
                motivo_bloqueio = f"Acesso negado para o perfil {user_role_enum.value} na rota {rota_acessada}. Essa operação exige: {permissoes_necessarias}"
                
                # Registra automaticamente a falha de segurança na tabela de logs!
                log_service.create_log(Log(
                    operation=LogOperation.CONNECT,
                    status=LogStatus.FAILED,
                    description=motivo_bloqueio,
                    device_id=None,
                    user_id=current_user.id,
                    date_hour=datetime.now()
                ))
                
                abort(403, description=f"Acesso negado. Esta operação exige um dos seguintes perfis: {permissoes_necessarias}")
            
            # -------------------------------------------------------------
            # Se passou por todas as barreiras, executa a rota normalmente!
            # -------------------------------------------------------------
            return f(*args, **kwargs)
        return decorated_function
    return decorator